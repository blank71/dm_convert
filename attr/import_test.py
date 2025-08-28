from absl.testing import absltest


class ImportTest(absltest.TestCase):

  def test_import_attrs(self):
    """Tests that attrs can be successfully imported without a dep on attr."""
    try:
      import attrs
    except Exception:  # gpylint: disable=broad-except
      raise


if __name__ == '__main__':
  absltest.main()
