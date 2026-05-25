import unittest
from pathlib import Path
from src.parser.universal_parser import UniversalParser

class TestUniversalParser(unittest.TestCase):
    def setUp(self):
        self.parser = UniversalParser()
        self.test_file = Path("test_dummy.js")
        self.test_file.write_text("""
function myPublicFunc() {
    console.log("hello");
}

function _myPrivateFunc() {
    console.log("private");
}

class MyPublicClass {
    constructor() {}
}

class _MyPrivateClass {
    constructor() {}
}
""")

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def test_parse_file(self):
        module = self.parser.parse_file(self.test_file)
        self.assertEqual(len(module.functions), 2)
        self.assertEqual(module.functions[0].name, "myPublicFunc")
        self.assertEqual(module.functions[0].visibility.value, "public")
        self.assertEqual(module.functions[1].name, "_myPrivateFunc")
        self.assertEqual(module.functions[1].visibility.value, "private")

        self.assertEqual(len(module.classes), 2)
        self.assertEqual(module.classes[0].name, "MyPublicClass")
        self.assertEqual(module.classes[0].visibility.value, "public")
        self.assertEqual(module.classes[1].name, "_MyPrivateClass")
        self.assertEqual(module.classes[1].visibility.value, "private")

if __name__ == '__main__':
    unittest.main()
