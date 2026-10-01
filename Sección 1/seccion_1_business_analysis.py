import pandas as pd


# 1. CARGA Y LIMPIEZA DE DATOS

# los archivos de datos se mantienen localmente y no se incluyen en el repositorio
orders = pd.read_csv(
    "data/orders.csv"
)

signups = pd.read_csv(
    "data/signups.csv"
)

# convierto las fechas a datetime para calcular diferencias de tiempo entre eventos
orders["order_date"] = pd.to_datetime(
    orders["order_date"],
    format="mixed"
)

signups["fecha_registro"] = pd.to_datetime(
    signups["fecha_registro"],
    format="mixed"
)


# 2. RENDIMIENTO GENERAL DEL NEGOCIO

# primero, analizo el negocio en general para entender el volumen de pedidos,
# clientes y facturacion


# 2.1. KPIS GENERALES

kpis = {
    "orders": orders["order_id"].nunique(),
    "unique_customers": orders["customer_id"].nunique(),
    "revenue": orders["total_value"].sum(),
    "average_order_value": orders["total_value"].mean()
}


# 2.2. RENDIMIENTO POR AÑO

# 2024 contiene datos solamente hasta octubre, por lo que no debe compararse
# directamente con el periodo completo de 2023

orders["year"] = orders["order_date"].dt.year

yearly = (
    orders
    .groupby("year")
    .agg(
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        revenue=("total_value", "sum"),
        AOV=("total_value", "mean")
    )
    .reset_index()
)


# 2.3. RENDIMIENTO POR CANAL

channel = (
    orders
    .groupby("channel")
    .agg(
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        revenue=("total_value", "sum"),
        AOV=("total_value", "mean")
    )
    .reset_index()
)


# 3. RENDIMIENTO A NIVEL CLIENTE

# agrupo los pedidos por cliente para analizar la frecuencia de compra,
# la facturacion y las fechas de compra

customer_metrics = (
    orders
    .groupby("customer_id")
    .agg(
        orders=("order_id", "nunique"),
        revenue=("total_value", "sum"),
        first_purchase=("order_date", "min"),
        last_purchase=("order_date", "max")
    )
    .reset_index()
)


# 3.1. KPIS DE CLIENTES

customer_kpis = {
    "customers": customer_metrics["customer_id"].nunique(),
    "average_revenue_per_customer": customer_metrics["revenue"].mean(),
    "average_orders_per_customer": customer_metrics["orders"].mean()
}


# 3.2. KPIS PARA EL DASHBOARD

dashboard_kpis = {
    "unique_customers": orders["customer_id"].nunique(),
    "orders": orders["order_id"].nunique(),
    "revenue": orders["total_value"].sum(),
    "AOV": orders["total_value"].mean(),
    "revenue_per_customer": (
        orders["total_value"].sum()
        / orders["customer_id"].nunique()
    )
}


# 4. CICLO DE VIDA DEL CLIENTE

# marco inicial del ciclo de vida:
# 1 compra -> primera compra
# 2-3 compras -> ciclo de vida temprano
# 4+ compras -> madurez


# 4.1. PRIMERA COMPRA

first_purchase = (
    orders
    .groupby("customer_id")["order_date"]
    .min()
    .reset_index()
    .rename(
        columns={"order_date": "first_purchase_date"}
    )
)


# 4.2. ACTIVACION

# combino los registros con la fecha de primera compra para medir
# el tiempo desde el registro hasta la primera compra

activation = (
    signups
    .merge(
        first_purchase,
        on="customer_id",
        how="left"
    )
)

activation["days_to_first_purchase"] = (
    activation["first_purchase_date"]
    - activation["fecha_registro"]
).dt.total_seconds() / (60 * 60 * 24)


# 4.3. KPIS DE ACTIVACION

activation_kpis = {
    "registered_users": activation["customer_id"].nunique(),
    "users_who_purchased": activation["first_purchase_date"].notna().sum(),
    "activation_rate": (
        activation["first_purchase_date"].notna().mean()
    ),
    "average_days_to_first_purchase": (
        activation["days_to_first_purchase"].mean()
    )
}

# la tasa de activacion se calcula solamente dentro de la base de registros.
# la base de pedidos contiene clientes que no aparecen en registros,
# por lo que este indicador no debe interpretarse como la tasa de activacion
# de todo el negocio.


# 4.4. DEFINICION INICIAL DEL CICLO DE VIDA

customer_metrics["lifecycle_stage"] = pd.cut(
    customer_metrics["orders"],
    bins=[0, 1, 3, float("inf")],
    labels=[
        "First purchase",
        "Early lifecycle",
        "Maturity"
    ]
)


# 4.5. DISTRIBUCION DE CLIENTES SEGUN NUMERO DE COMPRAS

purchase_groups = pd.cut(
    customer_metrics["orders"],
    bins=[0, 1, 2, 3, 4, 5, float("inf")],
    labels=[
        "1 purchase",
        "2 purchases",
        "3 purchases",
        "4 purchases",
        "5 purchases",
        "6+ purchases"
    ]
)

purchase_distribution = (
    customer_metrics
    .assign(purchase_group=purchase_groups)
    .groupby("purchase_group", observed=True)
    .agg(
        customers=("customer_id", "nunique"),
        revenue=("revenue", "sum")
    )
    .reset_index()
)

purchase_distribution["customer_percentage"] = (
    purchase_distribution["customers"]
    / purchase_distribution["customers"].sum()
)


# 4.6. TIEMPO ENTRE COMPRAS

orders_sorted = (
    orders
    .sort_values(["customer_id", "order_date"])
    .copy()
)

orders_sorted["previous_purchase"] = (
    orders_sorted
    .groupby("customer_id")["order_date"]
    .shift(1)
)

orders_sorted["days_between_purchases"] = (
    orders_sorted["order_date"]
    - orders_sorted["previous_purchase"]
).dt.total_seconds() / (60 * 60 * 24)

orders_sorted["purchase_number"] = (
    orders_sorted
    .groupby("customer_id")
    .cumcount() + 1
)

purchase_intervals = (
    orders_sorted
    .dropna(subset=["days_between_purchases"])
    .groupby("purchase_number")
    .agg(
        customers=("customer_id", "nunique"),
        avg_days=("days_between_purchases", "mean"),
        median_days=("days_between_purchases", "median")
    )
    .reset_index()
)


# 4.7. TRANSICIONES ENTRE COMPRAS

purchase_transitions = purchase_intervals.copy()

purchase_transitions["previous_customers"] = (
    purchase_transitions["customers"].shift(1)
)

# todos los clientes tienen al menos una compra, por lo que la segunda compra
# utiliza la cantidad total de clientes como poblacion inicial

purchase_transitions.loc[
    purchase_transitions["purchase_number"] == 2,
    "previous_customers"
] = customer_metrics["customer_id"].nunique()

purchase_transitions["transition_rate"] = (
    purchase_transitions["customers"]
    / purchase_transitions["previous_customers"]
)


# 4.8. ANALISIS DE COHORTES

# agrupo los clientes segun el mes de su primera compra

customer_metrics["first_purchase_month"] = (
    customer_metrics["first_purchase"]
    .dt.tz_localize(None)
    .dt.to_period("M")
)

cohorts = (
    customer_metrics
    .groupby("first_purchase_month")
    .agg(
        customers=("customer_id", "nunique"),
        avg_orders=("orders", "mean"),
        repeat_rate=("orders", lambda x: (x > 1).mean()),
        avg_revenue=("revenue", "mean")
    )
    .reset_index()
)


# 4.9. TIEMPO HASTA LA SEGUNDA COMPRA

first_to_second = orders_sorted[
    orders_sorted["purchase_number"] == 2
].copy()

first_to_second["time_to_second_purchase"] = pd.cut(
    first_to_second["days_between_purchases"],
    bins=[0, 7, 14, 30, 60, float("inf")],
    labels=[
        "0-7 dias",
        "8-14 dias",
        "15-30 dias",
        "31-60 dias",
        "60+ dias"
    ],
    include_lowest=True
)

second_purchase_timing = (
    first_to_second
    .groupby("time_to_second_purchase", observed=True)
    .agg(
        customers=("customer_id", "nunique")
    )
    .reset_index()
)

second_purchase_timing["customer_percentage"] = (
    second_purchase_timing["customers"]
    / second_purchase_timing["customers"].sum()
)


# 4.10. RETENCION TEMPORAL HASTA LA SEGUNDA COMPRA

observation_end = orders["order_date"].max()

first_purchase_analysis = customer_metrics[
    ["customer_id", "first_purchase"]
].copy()

first_purchase_analysis["days_observed"] = (
    observation_end - first_purchase_analysis["first_purchase"]
).dt.total_seconds() / (60 * 60 * 24)

second_purchase = orders_sorted[
    orders_sorted["purchase_number"] == 2
][
    ["customer_id", "order_date"]
].copy()

second_purchase = second_purchase.rename(
    columns={"order_date": "second_purchase"}
)

first_purchase_analysis = (
    first_purchase_analysis
    .merge(
        second_purchase,
        on="customer_id",
        how="left"
    )
)

first_purchase_analysis["days_to_second_purchase"] = (
    first_purchase_analysis["second_purchase"]
    - first_purchase_analysis["first_purchase"]
).dt.total_seconds() / (60 * 60 * 24)

retention_windows = []

for days in [7, 14, 30, 60]:

    # solo incluyo clientes que tengan suficiente tiempo de observacion
    # para completar la ventana analizada

    eligible = first_purchase_analysis[
        first_purchase_analysis["days_observed"] >= days
    ].copy()

    retained = eligible[
        eligible["days_to_second_purchase"].notna()
        & (eligible["days_to_second_purchase"] <= days)
    ]

    retention_windows.append({
        "window_days": days,
        "eligible_customers": eligible["customer_id"].nunique(),
        "repeat_customers": retained["customer_id"].nunique(),
        "retention_rate": (
            retained["customer_id"].nunique()
            / eligible["customer_id"].nunique()
        )
    })

temporal_retention = pd.DataFrame(retention_windows)


# 4.11. COMPRAS DURANTE LOS PRIMEROS 30 DIAS

early_lifecycle_30 = customer_metrics[
    customer_metrics["first_purchase"] <= (
        observation_end - pd.Timedelta(days=30)
    )
][
    ["customer_id", "first_purchase"]
].copy()

orders_30_days = (
    orders_sorted
    .merge(
        early_lifecycle_30,
        on="customer_id",
        how="inner"
    )
)

orders_30_days["days_since_first_purchase"] = (
    orders_30_days["order_date"]
    - orders_30_days["first_purchase"]
).dt.total_seconds() / (60 * 60 * 24)

orders_30_days = orders_30_days[
    (orders_30_days["days_since_first_purchase"] >= 0)
    & (orders_30_days["days_since_first_purchase"] <= 30)
]

orders_first_30 = (
    orders_30_days
    .groupby("customer_id")["order_id"]
    .nunique()
    .reset_index(name="orders_first_30_days")
)

orders_first_30["purchase_group"] = pd.cut(
    orders_first_30["orders_first_30_days"],
    bins=[0, 1, 2, 3, float("inf")],
    labels=[
        "1 purchase",
        "2 purchases",
        "3 purchases",
        "4+ purchases"
    ]
)

early_lifecycle_distribution = (
    orders_first_30
    .groupby("purchase_group", observed=True)
    .agg(
        customers=("customer_id", "nunique")
    )
    .reset_index()
)

early_lifecycle_distribution["customer_percentage"] = (
    early_lifecycle_distribution["customers"]
    / early_lifecycle_distribution["customers"].sum()
)


# 4.12. MADUREZ DEL CLIENTE

mature_customers = customer_metrics[
    customer_metrics["lifecycle_stage"] == "Maturity"
].copy()


# 4.13. RENDIMIENTO POR SEGMENTO DE CLIENTES

segments = customer_metrics.copy()

segments["segment"] = pd.cut(
    segments["orders"],
    bins=[0, 1, 3, 5, float("inf")],
    labels=[
        "One-time",
        "Early",
        "Engaged",
        "Loyal"
    ]
)

segment_performance = (
    segments
    .groupby("segment", observed=True)
    .agg(
        customers=("customer_id", "nunique"),
        orders=("orders", "sum"),
        revenue=("revenue", "sum")
    )
    .reset_index()
)

segment_performance["revenue_per_customer"] = (
    segment_performance["revenue"]
    / segment_performance["customers"]
)

segment_performance["orders_per_customer"] = (
    segment_performance["orders"]
    / segment_performance["customers"]
)


# 4.14. TASA DE CLIENTES RECURRENTES

repeat_customers = customer_metrics[
    customer_metrics["orders"] > 1
]

repeat_rate = (
    repeat_customers["customer_id"].nunique()
    / customer_metrics["customer_id"].nunique()
)


# 5. ANALISIS POR CANAL

# uso el canal de la primera compra como aproximacion al canal
# por el que ingreso el cliente


# 5.1. RENDIMIENTO DEL CLIENTE SEGUN EL CANAL DE PRIMERA COMPRA

first_purchase_channel = (
    orders_sorted
    .drop_duplicates("customer_id")
    [["customer_id", "channel"]]
)

customer_channel = (
    customer_metrics
    .merge(
        first_purchase_channel,
        on="customer_id",
        how="left"
    )
)

channel_customer_performance = (
    customer_channel
    .groupby("channel")
    .agg(
        customers=("customer_id", "nunique"),
        avg_orders=("orders", "mean"),
        avg_revenue=("revenue", "mean"),
        repeat_rate=("orders", lambda x: (x > 1).mean())
    )
    .reset_index()
)


# 5.2. CICLO DE VIDA SEGUN EL CANAL DE PRIMERA COMPRA

lifecycle_by_channel = (
    customer_channel
    .groupby(
        ["channel", "lifecycle_stage"],
        observed=True
    )
    .agg(
        customers=("customer_id", "nunique"),
        revenue=("revenue", "sum"),
        avg_orders=("orders", "mean")
    )
    .reset_index()
)

lifecycle_by_channel["customer_percentage"] = (
    lifecycle_by_channel["customers"]
    / lifecycle_by_channel
    .groupby("channel")["customers"]
    .transform("sum")
)


# 5.3. RETENCION A 30 DIAS POR CANAL

customer_retention = customer_channel[
    ["customer_id", "channel", "first_purchase"]
].copy()

customer_retention["days_observed"] = (
    observation_end - customer_retention["first_purchase"]
).dt.total_seconds() / (60 * 60 * 24)

second_purchase_channel = orders_sorted[
    orders_sorted["purchase_number"] == 2
][
    ["customer_id", "order_date"]
].copy()

second_purchase_channel = second_purchase_channel.rename(
    columns={"order_date": "second_purchase"}
)

customer_retention = (
    customer_retention
    .merge(
        second_purchase_channel,
        on="customer_id",
        how="left"
    )
)

customer_retention["days_to_second_purchase"] = (
    customer_retention["second_purchase"]
    - customer_retention["first_purchase"]
).dt.total_seconds() / (60 * 60 * 24)

# solo incluyo clientes con al menos 30 dias de observacion

eligible_30 = customer_retention[
    customer_retention["days_observed"] >= 30
].copy()

eligible_30["retained_30_days"] = (
    eligible_30["days_to_second_purchase"].notna()
    & (eligible_30["days_to_second_purchase"] <= 30)
)

retention_by_channel = (
    eligible_30
    .groupby("channel")
    .agg(
        customers=("customer_id", "nunique"),
        repeat_customers=("retained_30_days", "sum"),
        retention_30d=("retained_30_days", "mean")
    )
    .reset_index()
)


# 6. DATASETS PARA POWER BI

# estas tablas se mantienen en memoria y pueden exportarse localmente
# al momento de armar el dashboard de power bi.
#
# los archivos csv generados no deberian subirse a github porque
# contienen datos derivados a nivel cliente.


customer_dashboard = customer_channel[
    [
        "customer_id",
        "channel",
        "orders",
        "revenue",
        "first_purchase",
        "last_purchase",
        "lifecycle_stage"
    ]
].copy()

customer_dashboard["first_purchase_month"] = (
    customer_dashboard["first_purchase"]
    .dt.to_period("M")
    .astype(str)
)


retention_dashboard = retention_by_channel.copy()


lifecycle_kpis = pd.DataFrame({
    "kpi": [
        "Activation rate",
        "Second purchase rate",
        "30-day retention",
        "Days to first purchase",
        "% customers with 1 purchase",
        "% customers with 6+ purchases"
    ],
    "value": [
        activation_kpis["activation_rate"],
        repeat_rate,
        temporal_retention.loc[
            temporal_retention["window_days"] == 30,
            "retention_rate"
        ].iloc[0],
        activation_kpis["average_days_to_first_purchase"],
        (
            purchase_distribution.loc[
                purchase_distribution["purchase_group"] == "1 purchase",
                "customer_percentage"
            ].iloc[0]
        ),
        (
            purchase_distribution.loc[
                purchase_distribution["purchase_group"] == "6+ purchases",
                "customer_percentage"
            ].iloc[0]
        )
    ]
})


repeat_channel_dashboard = (
    retention_by_channel[
        ["channel", "retention_30d"]
    ]
    .merge(
        channel_customer_performance[
            ["channel", "repeat_rate"]
        ],
        on="channel",
        how="left"
    )
)


purchase_distribution_dashboard = (
    purchase_distribution.assign(
        segment=lambda df: df["purchase_group"].astype(str)
    )
    [
        ["segment", "customers"]
    ]
)


retention_2nd_dashboard = (
    temporal_retention[
        ["window_days", "retention_rate"]
    ]
    .rename(
        columns={
            "window_days": "days",
            "retention_rate": "retention"
        }
    )
)


monthly_dashboard = (
    orders
    .assign(
        month=orders["order_date"]
        .dt.to_period("M")
        .astype(str)
    )
    .groupby("month")
    .agg(
        orders=("order_id", "nunique"),
        revenue=("total_value", "sum")
    )
    .reset_index()
)