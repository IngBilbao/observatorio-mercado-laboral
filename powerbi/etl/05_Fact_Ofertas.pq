// ============================================================================
// Fact_Ofertas  (5000 ofertas — fact table principal)
// ----------------------------------------------------------------------------
// Origen:  data/processed/matriz_skills.csv
// Excluimos las 35 columnas skill_* (van a Fact_Skills_Oferta) y mantenemos
// solo los atributos de la oferta.
// ============================================================================
let
    Origen          = Csv.Document(
                        File.Contents(RutaProcesados & "matriz_skills.csv"),
                        [Delimiter = ",", Columns = null, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
                      ),
    Promovido       = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),

    // Quedarnos solo con columnas NO skill_*
    ColumnasAQuitar = List.Select(Table.ColumnNames(Promovido), each Text.StartsWith(_, "skill_")),
    SinSkills       = Table.RemoveColumns(Promovido, ColumnasAQuitar),

    // Tipos
    // CRITICO: el ultimo parametro "en-US" fuerza el parsing del PUNTO como
    // separador decimal. Sin esto, en una instancia de Power BI con locale
    // espanol, las latitudes/longitudes/salarios se interpretan incorrectamente
    // (el . se trata como separador de miles → 37.7749 se lee como 377749).
    Tipos           = Table.TransformColumnTypes(SinSkills, {
                        {"oferta_id",          type text},
                        {"fecha_publicacion",  type date},
                        {"titulo_cargo",       type text},
                        {"rol_normalizado",    type text},
                        {"nivel_experiencia",  type text},
                        {"anios_experiencia",  Int64.Type},
                        {"empresa",            type text},
                        {"ciudad",             type text},
                        {"pais",               type text},
                        {"codigo_pais",        type text},
                        {"latitud",            type number},
                        {"longitud",           type number},
                        {"modalidad",          type text},
                        {"tipo_contrato",      type text},
                        {"moneda_original",    type text},
                        {"salario_anual_usd",  type number},
                        {"n_skills",           Int64.Type},
                        {"descripcion",        type text},
                        {"fuente",             type text},
                        {"anio",               Int64.Type},
                        {"mes",                Int64.Type},
                        {"anio_mes",           type text}
                      }, "en-US"),

    // Columnas calculadas utiles
    SalarioMiles    = Table.AddColumn(Tipos, "salario_miles_usd", each [salario_anual_usd] / 1000, type number),
    BandaSalario    = Table.AddColumn(SalarioMiles, "banda_salarial", each
        if [salario_anual_usd] < 35000  then "1. Entry (<35K)"
        else if [salario_anual_usd] < 60000  then "2. Junior (35-60K)"
        else if [salario_anual_usd] < 90000  then "3. Mid (60-90K)"
        else if [salario_anual_usd] < 130000 then "4. Senior (90-130K)"
        else "5. Top (130K+)",
        type text
    ),

    // Drop columna skills_detectadas (queda redundante con Fact_Skills_Oferta)
    Final           = Table.RemoveColumns(BandaSalario, {"skills_detectadas"}, MissingField.Ignore)
in
    Final
