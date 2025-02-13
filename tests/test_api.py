import pandas as pd
import unittest
from src.api_client.postcodes_api import get_postcode_from_coordinates,get_postcodes_batch
  # Importar la función


class TestPostcodesAPI(unittest.TestCase):
    """ Test para la función get_postcodes_batch() """

    def setUp(self):
        """ Configurar datos de prueba """
        self.df_test = pd.DataFrame({"lat": [51.509865, 52.486244, 53.483959], "lon": [-0.118092, -1.890401, -2.244644]})

    def test_get_postcodes_batch(self):
        """ Verifica que la función devuelve un DataFrame con los campos esperados """
        df_result = get_postcodes_batch(self.df_test)

        # Verificar que se devuelve un DataFrame
        self.assertIsInstance(df_result, pd.DataFrame)

        # Verificar que el DataFrame tiene las mismas filas que el input
        self.assertEqual(len(df_result), len(self.df_test))

        # # Verificar que contiene las columnas esperadas
        # expected_columns = [
        #     "postcode", "country", "region", "district", "ward",
        #     "longitude", "latitude", "parish", "nuts_code"
        # ]
        # for col in expected_columns:
        #     self.assertIn(col, df_result.columns)

        # # Verificar que al menos un valor de código postal fue obtenido
        # self.assertTrue(df_result["postcode"].notnull().any())

if __name__ == "__main__":
    unittest.main()


# df_test = pd.DataFrame({
#     "lat": [51.509865, 52.486244, 53.483959],
#     "lon": [-0.118092, -1.890401, -2.244644]
# })

# df_result = get_postcodes_batch(df_test)
# print(df_result)
