// ============================================================================
// Dim_Ubicacion  (21 ciudades + region geografica)
// ----------------------------------------------------------------------------
// La derivamos a partir de Fact_Ofertas tomando los valores unicos.
// Asume que Fact_Ofertas ya esta cargado.
// ============================================================================
let
    Origen          = Fact_Ofertas,
    Seleccion       = Table.SelectColumns(Origen, {"ciudad", "pais", "codigo_pais", "latitud", "longitud"}),
    Distintos       = Table.Distinct(Seleccion),

    // Categoria regional para slicers / mapas
    ConRegion       = Table.AddColumn(Distintos, "region", each
        if [codigo_pais] = "WW" then "Remoto"
        else if List.Contains({"ES", "PT", "DE", "NL", "IE", "GB"}, [codigo_pais]) then "Europa"
        else if List.Contains({"US"}, [codigo_pais]) then "Norteamerica"
        else if List.Contains({"CO", "MX", "AR", "CL", "PE"}, [codigo_pais]) then "Latinoamerica"
        else "Otros",
        type text
    ),

    // Hub indicator (mercados con mayor poder adquisitivo)
    ConHub          = Table.AddColumn(ConRegion, "es_hub_tech", each
        List.Contains({"Nueva York", "San Francisco", "Londres", "Berlin", "Amsterdam", "Dublin"}, [ciudad]),
        type logical
    ),

    Orden           = Table.Sort(ConHub, {{"region", Order.Ascending}, {"pais", Order.Ascending}, {"ciudad", Order.Ascending}})
in
    Orden
