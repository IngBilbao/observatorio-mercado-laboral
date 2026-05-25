// ============================================================================
// Este archivo agrupa 3 consultas relacionadas con los modelos ML:
//   A) Dim_Clusters
//   B) Fact_ModeloSalarios       (predicciones salariales por oferta + residuo)
//   C) Fact_Coef_Salarios        (coeficientes del modelo — para grafico de impacto)
//
// COPIAR CADA BLOQUE COMO CONSULTA SEPARADA EN POWER BI.
// ============================================================================


// ─── A) Dim_Clusters ──────────────────────────────────────────────────────────
// Origen: data/outputs/clusters_resumen.csv  (4 filas, una por cluster)
let
    Origen      = Csv.Document(
                    File.Contents(RutaBase & "clusters_resumen.csv"),
                    [Delimiter = ",", Columns = null, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
                  ),
    Promovido   = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos       = Table.TransformColumnTypes(Promovido, {
                    {"cluster_id",            Int64.Type},
                    {"cluster_nombre",        type text},
                    {"n_ofertas",             Int64.Type},
                    {"pct_total",             type number},
                    {"rol_dominante",         type text},
                    {"salario_mediano_usd",   type number},
                    {"anios_exp_promedio",    type number},
                    {"top_skills",            type text}
                  })
in
    Tipos


// ─── B) Fact_ModeloSalarios ──────────────────────────────────────────────────
// Origen: data/outputs/modelo_salarios_predicciones.csv  (5000 filas)
// Se relaciona con Fact_Ofertas por oferta_id.
//
//   IMPORTANTE: copia este bloque como una nueva consulta separada.
let
    Origen      = Csv.Document(
                    File.Contents(RutaBase & "modelo_salarios_predicciones.csv"),
                    [Delimiter = ",", Columns = null, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
                  ),
    Promovido   = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos       = Table.TransformColumnTypes(Promovido, {
                    {"oferta_id",             type text},
                    {"rol_normalizado",       type text},
                    {"nivel_experiencia",     type text},
                    {"pais",                  type text},
                    {"salario_anual_usd",     type number},
                    {"salario_predicho_usd",  type number},
                    {"residuo_usd",           type number},
                    {"residuo_pct",           type number}
                  }),
    // Solo mantener lo nuevo (lo demas ya esta en Fact_Ofertas)
    Limpio      = Table.SelectColumns(Tipos, {"oferta_id", "salario_predicho_usd", "residuo_usd", "residuo_pct"})
in
    Limpio


// ─── C) Fact_Coef_Salarios ──────────────────────────────────────────────────
// Origen: data/outputs/modelo_salarios_coeficientes.csv  (54 filas)
// Para grafico "drivers de salario".
//
//   IMPORTANTE: copia este bloque como una nueva consulta separada.
let
    Origen      = Csv.Document(
                    File.Contents(RutaBase & "modelo_salarios_coeficientes.csv"),
                    [Delimiter = ",", Columns = null, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
                  ),
    Promovido   = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipos       = Table.TransformColumnTypes(Promovido, {
                    {"feature",     type text},
                    {"coef_log",    type number},
                    {"impacto_pct", type number}
                  }),
    // Categoria del feature para colorear/agrupar
    ConCategoria= Table.AddColumn(Tipos, "categoria_feature", each
        if Text.StartsWith([feature], "skill_") then "Skill"
        else if Text.StartsWith([feature], "nivel_experiencia_") then "Nivel"
        else if Text.StartsWith([feature], "pais_grp_") then "Pais"
        else if Text.StartsWith([feature], "modalidad_") then "Modalidad"
        else if Text.StartsWith([feature], "tipo_contrato_") then "Contrato"
        else if [feature] = "anios_experiencia" then "Experiencia"
        else "Otros",
        type text),
    // Etiqueta legible
    ConEtiqueta = Table.AddColumn(ConCategoria, "feature_legible", each
        Text.Replace(
            Text.Replace(
                Text.Replace(
                    Text.Replace(
                        Text.Replace([feature], "skill_", ""),
                        "nivel_experiencia_", "Nivel: "),
                    "pais_grp_", "Pais: "),
                "modalidad_", "Modalidad: "),
            "tipo_contrato_", "Contrato: "),
        type text)
in
    ConEtiqueta
