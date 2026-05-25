// ============================================================================
// Dim_Calendario  (tabla de calendario generada en M, sin CSV)
// ----------------------------------------------------------------------------
// Cubre desde 2024-01-01 hasta el final del forecast (2027-06-30).
// Marcar como "Tabla de fechas" en Power BI: Modelo → seleccionar tabla →
// "Marcar como tabla de fechas" → columna Fecha.
// ============================================================================
let
    FechaInicio = #date(2024, 1, 1),
    FechaFin    = #date(2027, 6, 30),
    Dias        = Duration.Days(FechaFin - FechaInicio) + 1,
    Lista       = List.Dates(FechaInicio, Dias, #duration(1, 0, 0, 0)),
    Tabla       = Table.FromList(Lista, Splitter.SplitByNothing(), {"Fecha"}),
    TipoFecha   = Table.TransformColumnTypes(Tabla, {{"Fecha", type date}}),
    Anio        = Table.AddColumn(TipoFecha, "Anio",        each Date.Year([Fecha]),         Int64.Type),
    Mes         = Table.AddColumn(Anio,      "Mes",         each Date.Month([Fecha]),        Int64.Type),
    MesNombre   = Table.AddColumn(Mes,       "MesNombre",   each Date.ToText([Fecha], "MMMM", "es-ES"), type text),
    MesCorto    = Table.AddColumn(MesNombre, "MesCorto",    each Date.ToText([Fecha], "MMM",  "es-ES"), type text),
    AnioMes     = Table.AddColumn(MesCorto,  "AnioMes",     each Date.ToText([Fecha], "yyyy-MM"),       type text),
    Trimestre   = Table.AddColumn(AnioMes,   "Trimestre",   each "Q" & Text.From(Date.QuarterOfYear([Fecha])), type text),
    AnioTrim    = Table.AddColumn(Trimestre, "AnioTrim",    each Text.From(Date.Year([Fecha])) & "-Q" & Text.From(Date.QuarterOfYear([Fecha])), type text),
    DiaSemana   = Table.AddColumn(AnioTrim,  "DiaSemana",   each Date.ToText([Fecha], "dddd", "es-ES"), type text),
    DiaNum      = Table.AddColumn(DiaSemana, "DiaSemanaNum",each Date.DayOfWeek([Fecha], Day.Monday) + 1, Int64.Type),
    EsFinSemana = Table.AddColumn(DiaNum,    "EsFinSemana", each Date.DayOfWeek([Fecha], Day.Monday) >= 5, type logical),
    InicioMes   = Table.AddColumn(EsFinSemana,"InicioMes",  each Date.StartOfMonth([Fecha]), type date)
in
    InicioMes
