
import pandas as pd


# 1. CARGA Y CALIDAD DE DATOS

# cargar base de campañas
campanas_base = pd.read_csv(
    "data/bd_campaigns_q3.csv"
)

# cargar base de ordenes
ordenes = pd.read_csv(
    "data/bd_orders.csv"
)

# convertir fechas
campanas_base["created_at"] = pd.to_datetime(
    campanas_base["created_at"],
    utc=True
)

ordenes["order_date"] = pd.to_datetime(
    ordenes["order_date"],
    format="mixed"
)


# 2. OBJETIVO 1 - ANALISIS DE CAMPAÑAS Y ENVIOS

# filtrar eventos de entrega para identificar los envios realizados
entregados = campanas_base[
    campanas_base["metric"] == "delivered"
]

total_campanas = campanas_base["campaign_id"].nunique()
total_entregados = len(entregados)
usuarios_unicos = entregados["customer_id"].nunique()

# promedio de envios entregados por usuario
envios_por_usuario = total_entregados / usuarios_unicos

print("Campañas:", total_campanas)
print("Envíos entregados:", total_entregados)
print("Usuarios comunicados:", usuarios_unicos)
print("Envíos por usuario:", envios_por_usuario)


# metricas generales de engagement
aperturas = campanas_base[
    campanas_base["metric"] == "opened"
]

clicks = campanas_base[
    campanas_base["metric"] == "clicked"
]

total_aperturas = len(aperturas)
total_clicks = len(clicks)

tasa_apertura = total_aperturas / total_entregados
tasa_click = total_clicks / total_entregados
tasa_click_apertura = total_clicks / total_aperturas

print("Aperturas:", total_aperturas)
print("Clicks:", total_clicks)
print("Tasa de apertura:", tasa_apertura)
print("Tasa de click:", tasa_click)
print("Tasa de click sobre apertura:", tasa_click_apertura)


# metricas por campaña
#  algunas campañas presentan inconsistencias entre eventos de entrega, apertura y click. Por eso las tasas se calculan solo cuando existen registros de delivered.

campanas = (
    campanas_base
    .groupby(["campaign_id", "campaign_name"])
    .agg(
        envios=("metric", lambda x: (x == "delivered").sum()),
        aperturas=("metric", lambda x: (x == "opened").sum()),
        clicks=("metric", lambda x: (x == "clicked").sum()),
        usuarios=("customer_id", "nunique")
    )
    .reset_index()
)

campanas["tasa_apertura"] = (
    campanas["aperturas"] / campanas["envios"]
).where(campanas["envios"] > 0)

campanas["tasa_click"] = (
    campanas["clicks"] / campanas["envios"]
).where(campanas["envios"] > 0)

campanas = campanas.sort_values(
    "envios",
    ascending=False
)


# usuarios que recibieron al menos una comunicación
usuarios_comunicados = (
    entregados["customer_id"]
    .drop_duplicates()
)

print("Usuarios comunicados:", len(usuarios_comunicados))


# usuarios comunicados que realizaron al menos una compra
usuarios_compraron = ordenes[
    ordenes["customer_id"].isin(usuarios_comunicados)
]["customer_id"].nunique()

tasa_compra_comunicados = (
    usuarios_compraron / len(usuarios_comunicados)
)

print(
    "Tasa de compra de usuarios comunicados:",
    tasa_compra_comunicados
)

# este resultado muestra cuántos usuarios comunicados compraron durante el periodo analizado, pero no permite atribuir la compra a las campañas porque todavía no se considera el momento de la compra.


# primera comunicación recibida por cada usuario
primera_comunicacion = (
    entregados
    .groupby("customer_id")["created_at"]
    .min()
    .reset_index()
    .rename(
        columns={
            "created_at": "fecha_primera_comunicacion"
        }
    )
)


# unir la fecha de primera comunicación con las ordenes
ordenes_comunicados = ordenes.merge(
    primera_comunicacion,
    on="customer_id",
    how="inner"
)


# conservar compras realizadas después de la primera comunicación
compras_post_comunicacion = ordenes_comunicados[
    ordenes_comunicados["order_date"]
    > ordenes_comunicados["fecha_primera_comunicacion"]
]

usuarios_compraron_post = (
    compras_post_comunicacion["customer_id"].nunique()
)

tasa_compra_post_comunicacion = (
    usuarios_compraron_post / len(usuarios_comunicados)
)

ventas_post_comunicacion = (
    compras_post_comunicacion["total_value"].sum()
)

ticket_post_comunicacion = (
    compras_post_comunicacion["total_value"].mean()
)

ticket_general = ordenes["total_value"].mean()

print(
    "Órdenes posteriores a la comunicación:",
    len(compras_post_comunicacion)
)

print(
    "Usuarios que compraron después:",
    usuarios_compraron_post
)

print(
    "Tasa de compra posterior:",
    tasa_compra_post_comunicacion
)

print(
    "Ventas posteriores:",
    ventas_post_comunicacion
)

print(
    "Ticket promedio post comunicación:",
    ticket_post_comunicacion
)

print(
    "Ticket promedio general:",
    ticket_general
)


# cantidad promedio de compras posteriores por usuario
ordenes_por_usuario_post = (
    compras_post_comunicacion
    .groupby("customer_id")["order_id"]
    .nunique()
)

print(
    "Promedio de órdenes posteriores por usuario:",
    ordenes_por_usuario_post.mean()
)


# distribución de usuarios según cantidad de compras posteriores
frecuencia_post_comunicacion = (
    ordenes_por_usuario_post
    .value_counts()
    .sort_index()
)

print(frecuencia_post_comunicacion)


# campañas con un volumen mínimo de envios
campanas_volumen = campanas[
    campanas["envios"] >= 500
].copy()

campanas_volumen = campanas_volumen.sort_values(
    "tasa_click",
    ascending=False
)


# análisis específico de campañas de incentivo
for id_campana in [44, 45, 46]:

    campana = entregados[
        entregados["campaign_id"] == id_campana
    ].copy()

    usuarios_campana = (
        campana["customer_id"]
        .drop_duplicates()
    )

    fecha_campana = (
        campana
        .groupby("customer_id")["created_at"]
        .min()
        .reset_index()
        .rename(
            columns={
                "created_at": "fecha_campana"
            }
        )
    )

    ordenes_campana = ordenes.merge(
        fecha_campana,
        on="customer_id",
        how="inner"
    )

    compras_post = ordenes_campana[
        ordenes_campana["order_date"]
        > ordenes_campana["fecha_campana"]
    ]

    usuarios_compraron = (
        compras_post["customer_id"].nunique()
    )

    tasa_compra = (
        usuarios_compraron / len(usuarios_campana)
    )

    ventas_post = (
        compras_post["total_value"].sum()
    )

    ordenes_post = (
        compras_post["order_id"].nunique()
    )

    ticket_post = (
        compras_post["total_value"].mean()
    )

    print(
        f"\nCampaña {id_campana}"
    )

    print(
        "Usuarios:",
        len(usuarios_campana)
    )

    print(
        "Usuarios que compraron después:",
        usuarios_compraron
    )

    print(
        "Tasa de compra posterior:",
        tasa_compra
    )

    print(
        "Órdenes posteriores:",
        ordenes_post
    )

    print(
        "Ventas posteriores:",
        ventas_post
    )

    print(
        "Ticket promedio:",
        ticket_post
    )


# estas métricas muestran una asociación temporal entre las campañas y las compras posteriores. Sin embargo, no permiten estimar el efecto causal de las campañas porque no se dispone de un grupo de control.


# 3. OBJETIVO 2 - ACTIVACION

registros = pd.read_csv(
    "data/BD_signups.csv"
)

registros["fecha_registro"] = pd.to_datetime(
    registros["fecha_registro"],
    format="mixed"
)

usuarios_registro = (
    registros["customer_id"]
    .drop_duplicates()
)

usuarios_compraron = ordenes[
    ordenes["customer_id"].isin(usuarios_registro)
]["customer_id"].nunique()

tasa_activacion = (
    usuarios_compraron / len(usuarios_registro)
)

print(
    "\nUsuarios registrados:",
    len(usuarios_registro)
)

print(
    "Usuarios activados:",
    usuarios_compraron
)

print(
    "Tasa de activación:",
    tasa_activacion
)


# primera compra de cada usuario registrado
primera_compra = (
    ordenes[
        ordenes["customer_id"].isin(usuarios_registro)
    ]
    .groupby("customer_id")["order_date"]
    .min()
    .reset_index()
    .rename(
        columns={
            "order_date": "fecha_primera_compra"
        }
    )
)


# unir registro y primera compra
activacion = (
    registros[
        ["customer_id", "fecha_registro"]
    ]
    .drop_duplicates("customer_id")
    .merge(
        primera_compra,
        on="customer_id",
        how="inner"
    )
)


# calcular días hasta la primera compra
activacion["dias_hasta_primera_compra"] = (
    activacion["fecha_primera_compra"]
    - activacion["fecha_registro"]
).dt.total_seconds() / (60 * 60 * 24)

print(
    "Promedio de días hasta primera compra:",
    activacion["dias_hasta_primera_compra"].mean()
)


# agrupar usuarios según tiempo hasta primera compra
activacion["grupo_dias"] = pd.cut(
    activacion["dias_hasta_primera_compra"],
    bins=[-1, 7, 14, 30, 60, float("inf")],
    labels=[
        "0-7 días",
        "8-14 días",
        "15-30 días",
        "31-60 días",
        "60+ días"
    ]
)

distribucion_activacion = (
    activacion["grupo_dias"]
    .value_counts()
    .sort_index()
)

print(distribucion_activacion)


# usuarios registrados que todavía no realizaron una compra
usuarios_no_activados = (
    len(usuarios_registro) - usuarios_compraron
)

print(
    "Usuarios no activados:",
    usuarios_no_activados
)

print(
    "Porcentaje no activado:",
    usuarios_no_activados / len(usuarios_registro)
)


# presupuesto de referencia para la estrategia de activación
facturacion = ordenes["total_value"].sum()

presupuesto_activacion = (
    facturacion * 0.15
)

print(
    "Facturación analizada:",
    facturacion
)

print(
    "Presupuesto de referencia para activación:",
    presupuesto_activacion
)


# el presupuesto se toma como un supuesto para dimensionar la estrategia.
# para medir el retorno incremental real sería necesario utilizar grupos
# de control y comparar usuarios expuestos contra usuarios similares
# que no recibieron el incentivo.


# 4. OBJETIVO 3 - FRECUENCIA DE COMPRA

# cantidad de compras por usuario
compras_por_usuario = (
    ordenes
    .groupby("customer_id")["order_id"]
    .nunique()
    .reset_index()
    .rename(
        columns={
            "order_id": "cantidad_compras"
        }
    )
)


# agrupar usuarios según cantidad de compras
compras_por_usuario["grupo_compras"] = pd.cut(
    compras_por_usuario["cantidad_compras"],
    bins=[0, 1, 2, 3, 4, 5, float("inf")],
    labels=[
        "1 compra",
        "2 compras",
        "3 compras",
        "4 compras",
        "5 compras",
        "6+ compras"
    ]
)

frecuencia = (
    compras_por_usuario["grupo_compras"]
    .value_counts()
    .sort_index()
)

print("\nDistribución de frecuencia:")
print(frecuencia)


# transición de primera a segunda compra
usuarios_2_o_mas = (
    compras_por_usuario["cantidad_compras"] >= 2
).sum()

usuarios_1_compra = (
    compras_por_usuario["cantidad_compras"] == 1
).sum()

tasa_1_2 = (
    usuarios_2_o_mas
    / (usuarios_2_o_mas + usuarios_1_compra)
)

print(
    "Usuarios que llegaron a 2 compras:",
    usuarios_2_o_mas
)

print(
    "Usuarios que quedaron en 1 compra:",
    usuarios_1_compra
)

print(
    "Tasa de transición 1 a 2:",
    tasa_1_2
)


# ordenar las órdenes cronológicamente por usuario
ordenes_ordenadas = (
    ordenes
    .sort_values(
        ["customer_id", "order_date"]
    )
    .copy()
)

ordenes_ordenadas["numero_compra"] = (
    ordenes_ordenadas
    .groupby("customer_id")
    .cumcount()
    + 1
)


# identificar primera y segunda compra
primera_y_segunda = ordenes_ordenadas[
    ordenes_ordenadas["numero_compra"].isin([1, 2])
].copy()

fechas_compras = (
    primera_y_segunda
    .pivot(
        index="customer_id",
        columns="numero_compra",
        values="order_date"
    )
    .reset_index()
)

fechas_compras["dias_entre_compras"] = (
    fechas_compras[2]
    - fechas_compras[1]
).dt.total_seconds() / (60 * 60 * 24)

tiempo_segunda_compra = fechas_compras[
    fechas_compras["dias_entre_compras"].notna()
].copy()

print(
    "Promedio de días hasta segunda compra:",
    tiempo_segunda_compra["dias_entre_compras"].mean()
)

print(
    "Mediana de días hasta segunda compra:",
    tiempo_segunda_compra["dias_entre_compras"].median()
)


# agrupar tiempo hasta segunda compra
tiempo_segunda_compra["grupo_dias"] = pd.cut(
    tiempo_segunda_compra["dias_entre_compras"],
    bins=[-1, 7, 14, 30, 60, float("inf")],
    labels=[
        "0-7 días",
        "8-14 días",
        "15-30 días",
        "31-60 días",
        "60+ días"
    ]
)

distribucion_segunda = (
    tiempo_segunda_compra["grupo_dias"]
    .value_counts()
    .sort_index()
)

print(distribucion_segunda)


# frecuencia de compra según el canal de la primera compra
primera_compra_canal = (
    ordenes_ordenadas
    .groupby("customer_id")
    .first()
    .reset_index()
)

frecuencia_canal = (
    compras_por_usuario
    .merge(
        primera_compra_canal[
            ["customer_id", "channel"]
        ],
        on="customer_id",
        how="left"
    )
    .groupby("channel")
    .agg(
        usuarios=("customer_id", "nunique"),
        compras_promedio=("cantidad_compras", "mean")
    )
    .reset_index()
)


# cantidad de usuarios que repitieron la compra por canal
repetidores_canal = (
    compras_por_usuario
    .merge(
        primera_compra_canal[
            ["customer_id", "channel"]
        ],
        on="customer_id",
        how="left"
    )
    .groupby("channel")
    .agg(
        usuarios_repetidores=(
            "cantidad_compras",
            lambda x: (x >= 2).sum()
        )
    )
    .reset_index()
)

frecuencia_canal = frecuencia_canal.merge(
    repetidores_canal,
    on="channel",
    how="left"
)

frecuencia_canal["tasa_repeticion"] = (
    frecuencia_canal["usuarios_repetidores"]
    / frecuencia_canal["usuarios"]
)

print("\nFrecuencia por canal:")
print(frecuencia_canal)


# analizar las transiciones entre niveles de compra
transiciones = []

for compra_actual in range(1, 6):

    usuarios_actual = (
        compras_por_usuario["cantidad_compras"]
        >= compra_actual
    ).sum()

    usuarios_siguiente = (
        compras_por_usuario["cantidad_compras"]
        >= compra_actual + 1
    ).sum()

    tasa = (
        usuarios_siguiente / usuarios_actual
    )

    transiciones.append(
        {
            "transicion": (
                f"{compra_actual} a {compra_actual + 1}"
            ),
            "usuarios_actual": usuarios_actual,
            "usuarios_siguiente": usuarios_siguiente,
            "tasa": tasa
        }
    )

transiciones = pd.DataFrame(transiciones)

print("\nTransiciones:")
print(transiciones)


# la principal oportunidad de frecuencia se encuentra entre la primera y segunda compra. La estrategia debería priorizar este momento del lifecycle, especialmente durante los primeros 30 días.
