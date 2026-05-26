// ============================================================================
// Fact_Predicciones  (forecast Prophet — formato largo)
// ----------------------------------------------------------------------------
// Origen:  data/outputs/predicciones_skills.csv  (432 filas)
// Cada fila: (mes, skill, valor central, banda inferior, banda superior, ¿es historico?)
// ============================================================================
let
    Origen          = Csv.Document(
                        File.Contents(RutaBase & "predicciones_skills.csv"),
                        [Delimiter = ",", Columns = null, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
                      ),
    Promovido       = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),

    // "en-US" fuerza el punto como separador decimal (ver 05_Fact_Ofertas.pq)
    Tipos           = Table.TransformColumnTypes(Promovido, {
                        {"ds",         type date},
                        {"yhat",       type number},
                        {"yhat_lower", type number},
                        {"yhat_upper", type number},
                        {"skill",      type text},
                        {"historico",  type logical}
                      }, "en-US"),

    Renombrado      = Table.RenameColumns(Tipos, {
                        {"ds",         "fecha"},
                        {"yhat",       "prediccion"},
                        {"yhat_lower", "banda_inferior"},
                        {"yhat_upper", "banda_superior"}
                      }),

    // Columna que distingue facilmente para visuales
    Tipo            = Table.AddColumn(Renombrado, "tipo_serie", each if [historico] then "Historico" else "Forecast", type text)
in
    Tipo
