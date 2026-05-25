// ============================================================================
// Fact_Skills_Oferta  (unpivot de skill_* — bridge entre Fact_Ofertas y Dim_Skills)
// ----------------------------------------------------------------------------
// Origen:  data/processed/matriz_skills.csv  (mismas filas, otras columnas)
// Resultado: ~32000 filas (5000 ofertas × ~6.4 skills promedio)
// ============================================================================
let
    Origen          = Csv.Document(
                        File.Contents(RutaProcesados & "matriz_skills.csv"),
                        [Delimiter = ",", Columns = null, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
                      ),
    Promovido       = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),

    // Mantener oferta_id + todas las columnas skill_*
    SkillCols       = List.Select(Table.ColumnNames(Promovido), each Text.StartsWith(_, "skill_")),
    Seleccion       = Table.SelectColumns(Promovido, {"oferta_id"} & SkillCols),

    // Unpivot: una fila por (oferta_id, skill_id, valor)
    Unpivoted       = Table.UnpivotOtherColumns(Seleccion, {"oferta_id"}, "skill_id", "tiene_skill"),

    // Filtrar solo los TRUE
    SoloPresentes   = Table.SelectRows(Unpivoted, each Text.Lower(Text.From([tiene_skill])) = "true"),

    // Limpiar — quedarnos con [oferta_id, skill_id]
    Limpio          = Table.SelectColumns(SoloPresentes, {"oferta_id", "skill_id"}),

    Tipos           = Table.TransformColumnTypes(Limpio, {
                        {"oferta_id", type text},
                        {"skill_id",  type text}
                      })
in
    Tipos
