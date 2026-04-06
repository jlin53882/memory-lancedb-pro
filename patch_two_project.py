from pathlib import Path

# Patch 1: PortfolioView
p = Path(r'C:\Users\admin\Desktop\two_project\src\views\portfolio_view.py')
txt = p.read_text(encoding='utf-8')
txt = txt.replace('self._date_picker.pick_date()', 'self._date_picker.open()')
txt = txt.replace(
    'selected = self._date_picker.selected_date\n        if selected is None:\n            return\n        target = getattr(self, "_date_target", None)\n        if target:\n            target.value = selected.strftime("%Y-%m-%d")\n            target.update()\n            target = None',
    'selected = self._date_picker.value\n        if selected is None:\n            return\n        target = getattr(self, "_date_target", None)\n        if target:\n            target.value = selected.strftime("%Y-%m-%d")\n            target.update()\n            self._date_target = None'
)
p.write_text(txt, encoding='utf-8')

# Patch 2: WorkView
p = Path(r'C:\Users\admin\Desktop\two_project\src\views\work_view.py')
txt = p.read_text(encoding='utf-8')
txt = txt.replace('self._date_picker_add.selected_date', 'self._date_picker_add.value')
txt = txt.replace('self._date_picker_edit.selected_date', 'self._date_picker_edit.value')
txt = txt.replace('self._date_picker_add.pick_date()', 'self._date_picker_add.open()')
txt = txt.replace('self._date_picker_edit.pick_date()', 'self._date_picker_edit.open()')
p.write_text(txt, encoding='utf-8')

# Patch 3: UIFeedback SnackBar display
p = Path(r'C:\Users\admin\Desktop\two_project\src\state\ui_feedback.py')
txt = p.read_text(encoding='utf-8')
txt = txt.replace('        snack = ft.SnackBar(content=ft.Text(text, color=ft.Colors.WHITE), bgcolor=bgcolor)\n        page.overlay.append(snack)\n        snack.open = True\n        page.update()\n', '        snack = ft.SnackBar(content=ft.Text(text, color=ft.Colors.WHITE), bgcolor=bgcolor)\n        page.show_dialog(snack)\n')
p.write_text(txt, encoding='utf-8')
