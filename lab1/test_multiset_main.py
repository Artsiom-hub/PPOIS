import unittest
from multiset import Multiset
import io
import sys
from unittest.mock import patch
import multimnoghestvo  # имя файла, где лежит твой код (переименуй под себя)


class TestMainMultiset(unittest.TestCase):

    def test_main_prints_correct_output(self):
        # захватываем stdout
        buffer = io.StringIO()
        with patch('sys.stdout', buffer):
            multimnoghestvo.main()

        output = buffer.getvalue()

        # Проверяем ключевые строки
        self.assertIn("Множество m1:", output)
        self.assertIn("Множество m2:", output)
        self.assertIn("Объединение:", output)
        self.assertIn("Пересечение:", output)
        self.assertIn("Разность:", output)
        self.assertIn("Мощность m1:", output)
        self.assertIn("Булеан m1:", output)

    def test_main_does_not_raise(self):
        # Просто проверяем, что main() не падает
        try:
            multimnoghestvo.main()
        except Exception as e:
            self.fail(f"main() raised an exception: {e}")

    def test_m1_parsed_correctly(self):
        m1 = Multiset("{a, a, c, {a, b, b}, {}, {a, {c, c}}}")
        # Простейшие проверки структуры:
        self.assertIn("a", str(m1))
        self.assertIn("c", str(m1))

    def test_m2_parsed_correctly(self):
        m2 = Multiset("{a, c, d}")
        self.assertEqual(m2.size(), 3)

    def test_operations(self):
        m1 = Multiset("{a, a, c, {a, b, b}, {}, {a, {c, c}}}")
        m2 = Multiset("{a, c, d}")

        union_res = m1 + m2
        inter_res = m1 * m2
        diff_res = m1 - m2

        self.assertIsInstance(union_res, Multiset)
        self.assertIsInstance(inter_res, Multiset)
        self.assertIsInstance(diff_res, Multiset)

        # минимальная содержательная проверка
        self.assertTrue(union_res.size() >= m1.size())
        self.assertTrue(inter_res.size() <= m1.size())




    def test_import_does_not_run_main(self):
        """Гарантия, что при импорте код НЕ вызывает main (в отличие от твоего tictactoe)"""
        with patch("sys.stdout", new=io.StringIO()) as buf:
            # повторный импорт НЕ должен печатать результаты main()
            import importlib
            importlib.reload(multimnoghestvo)
            output = buf.getvalue()

        # ничего не должно быть напечатано
        self.assertEqual(output.strip(), "")
