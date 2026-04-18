import flet as ft
import json
import os
from datetime import datetime
from collections import defaultdict


class OvertimeApp:
    def __init__(self):
        self.data_file = "overtime_data.json"
        self.employees_file = "employees.json"
        self.overtime_data = self.load_data()
        self.employees = self.load_employees()
        self.current_filter_employee = "全部"
        self.start_date = None
        self.end_date = None
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.overtime_data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def load_employees(self):
        if os.path.exists(self.employees_file):
            try:
                with open(self.employees_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_employees(self):
        try:
            with open(self.employees_file, 'w', encoding='utf-8') as f:
                json.dump(self.employees, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def get_coefficient(self, overtime_type):
        coefficients = {"工作日": 1.0, "周末": 1.5, "节假日": 3.0}
        return coefficients.get(overtime_type, 1.0)
    
    def get_filtered_data(self):
        filtered = self.overtime_data
        if self.start_date:
            filtered = [r for r in filtered if r['date'] >= self.start_date]
        if self.end_date:
            filtered = [r for r in filtered if r['date'] <= self.end_date]
        if self.current_filter_employee != "全部":
            filtered = [r for r in filtered if r['employee'] == self.current_filter_employee]
        return filtered
    
    def get_statistics(self, data=None):
        if data is None:
            data = self.get_filtered_data()
        if not data:
            return None
        
        employee_stats = defaultdict(lambda: {"hours": 0, "converted": 0, "count": 0})
        for record in data:
            emp = record['employee']
            employee_stats[emp]['hours'] += record['hours']
            employee_stats[emp]['converted'] += record['converted_hours']
            employee_stats[emp]['count'] += 1
        
        type_stats = defaultdict(lambda: {"hours": 0, "count": 0})
        for record in data:
            typ = record['type']
            type_stats[typ]['hours'] += record['hours']
            type_stats[typ]['count'] += 1
        
        return {
            "total_count": len(data),
            "total_hours": sum(r['hours'] for r in data),
            "total_converted": sum(r['converted_hours'] for r in data),
            "employee_stats": dict(employee_stats),
            "type_stats": dict(type_stats)
        }
    
    def add_record(self, employee, date, hours, overtime_type):
        if not employee or employee not in self.employees:
            return False, "请选择有效的员工"
        if not date:
            return False, "请填写日期"
        if hours <= 0:
            return False, "加班时长必须大于0"
        
        coefficient = self.get_coefficient(overtime_type)
        converted_hours = hours * coefficient
        record_id = len(self.overtime_data) + 1
        
        record = {
            "id": record_id,
            "employee": employee,
            "date": date,
            "hours": hours,
            "type": overtime_type,
            "coefficient": coefficient,
            "converted_hours": converted_hours,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.overtime_data.append(record)
        self.save_data()
        return True, f"已添加 {employee} 的加班记录"
    
    def delete_record(self, record_id):
        self.overtime_data = [r for r in self.overtime_data if r['id'] != record_id]
        self.save_data()
        return True
    
    def add_employee(self, name):
        name = name.strip()
        if not name:
            return False, "请输入员工姓名"
        if name in self.employees:
            return False, "员工已存在"
        self.employees.append(name)
        self.save_employees()
        return True, f"已添加员工: {name}"
    
    def delete_employee(self, name):
        has_records = any(r['employee'] == name for r in self.overtime_data)
        if has_records:
            return False, f"{name} 有加班记录，无法删除"
        self.employees.remove(name)
        self.save_employees()
        return True, f"已删除员工: {name}"


def main(page: ft.Page):
    page.title = "员工加班统计"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 400
    page.window_height = 700
    
    app = OvertimeApp()
    
    # 颜色
    BLUE = ft.Colors.BLUE_500
    GREEN = ft.Colors.GREEN_500
    ORANGE = ft.Colors.ORANGE_500
    RED = ft.Colors.RED_500
    
    # 创建控件
    employee_dropdown = ft.Dropdown(label="员工", width=150)
    date_field = ft.TextField(label="日期", value=datetime.now().strftime("%Y-%m-%d"), width=130)
    hours_field = ft.TextField(label="时长", width=100, keyboard_type=ft.KeyboardType.NUMBER)
    type_dropdown = ft.Dropdown(
        label="类型",
        options=[ft.dropdown.Option("工作日"), ft.dropdown.Option("周末"), ft.dropdown.Option("节假日")],
        value="工作日",
        width=100
    )
    new_employee_field = ft.TextField(label="新员工", width=150)
    filter_dropdown = ft.Dropdown(label="筛选", width=120)
    start_date_field = ft.TextField(label="开始", width=120)
    end_date_field = ft.TextField(label="结束", width=120)
    
    # 统计显示
    total_count_text = ft.Text("0", size=24, weight=ft.FontWeight.BOLD, color=BLUE)
    total_hours_text = ft.Text("0h", size=24, weight=ft.FontWeight.BOLD, color=GREEN)
    total_converted_text = ft.Text("0h", size=24, weight=ft.FontWeight.BOLD, color=ORANGE)
    stats_text = ft.Text("", size=12)
    
    # 记录列表
    records_list = ft.ListView(expand=True, spacing=8, height=350)
    
    def refresh_data():
        refresh_records_list()
        refresh_statistics()
        refresh_employee_dropdowns()
    
    def refresh_records_list():
        records_list.controls.clear()
        filtered_data = app.get_filtered_data()
        
        if not filtered_data:
            records_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(name="inbox", size=60, color=ft.Colors.GREY_400),
                        ft.Text("暂无记录", size=14, color=ft.Colors.GREY_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30,
                )
            )
        else:
            for record in filtered_data:
                record_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.CircleAvatar(
                                    content=ft.Text(record['employee'][0]),
                                    bgcolor=BLUE,
                                    width=35,
                                    height=35,
                                ),
                                ft.Column([
                                    ft.Text(record['employee'], weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(record['date'], size=11, color=ft.Colors.GREY_600),
                                ], spacing=1),
                                ft.Container(expand=True),
                                ft.IconButton(
                                    icon="delete",
                                    icon_size=20,
                                    icon_color=RED,
                                    on_click=lambda e, rid=record['id']: delete_record(rid),
                                ),
                            ]),
                            ft.Row([
                                ft.Text(f"时长: {record['hours']}h", size=12),
                                ft.Text(f"类型: {record['type']}", size=12),
                                ft.Text(f"折算: {record['converted_hours']:.0f}h", size=12, weight=ft.FontWeight.BOLD, color=BLUE),
                            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                        ]),
                        padding=10,
                    ),
                )
                records_list.controls.append(record_card)
        page.update()
    
    def refresh_statistics():
        stats = app.get_statistics()
        if stats:
            total_count_text.value = str(stats['total_count'])
            total_hours_text.value = f"{stats['total_hours']:.0f}h"
            total_converted_text.value = f"{stats['total_converted']:.0f}h"
            stats_text.value = f"员工: {len(stats['employee_stats'])}人"
        else:
            total_count_text.value = "0"
            total_hours_text.value = "0h"
            total_converted_text.value = "0h"
            stats_text.value = "暂无数据"
        page.update()
    
    def refresh_employee_dropdowns():
        options = [ft.dropdown.Option(emp) for emp in app.employees]
        employee_dropdown.options = options
        if app.employees:
            employee_dropdown.value = app.employees[0]
        filter_options = [ft.dropdown.Option("全部")] + [ft.dropdown.Option(emp) for emp in app.employees]
        filter_dropdown.options = filter_options
        page.update()
    
    def delete_record(record_id):
        app.delete_record(record_id)
        refresh_data()
        show_snackbar("记录已删除")
    
    def add_record_click(e):
        employee = employee_dropdown.value
        date = date_field.value
        try:
            hours = float(hours_field.value) if hours_field.value else 0
        except ValueError:
            hours = 0
        overtime_type = type_dropdown.value
        
        success, msg = app.add_record(employee, date, hours, overtime_type)
        if success:
            hours_field.value = ""
            refresh_data()
        show_snackbar(msg)
    
    def add_employee_click(e):
        name = new_employee_field.value
        success, msg = app.add_employee(name)
        if success:
            new_employee_field.value = ""
            refresh_employee_dropdowns()
        show_snackbar(msg)
    
    def delete_employee_click(e):
        selected = filter_dropdown.value
        if not selected or selected == "全部":
            show_snackbar("请先选择要删除的员工")
            return
        success, msg = app.delete_employee(selected)
        if success:
            refresh_employee_dropdowns()
            refresh_data()
        show_snackbar(msg)
    
    def apply_filter(e):
        app.current_filter_employee = filter_dropdown.value
        app.start_date = start_date_field.value if start_date_field.value else None
        app.end_date = end_date_field.value if end_date_field.value else None
        refresh_data()
    
    def reset_filter(e):
        filter_dropdown.value = "全部"
        start_date_field.value = ""
        end_date_field.value = ""
        app.current_filter_employee = "全部"
        app.start_date = None
        app.end_date = None
        refresh_data()
    
    def show_snackbar(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg))
        page.snack_bar.open = True
        page.update()
    
    refresh_employee_dropdowns()
    
    # 布局
    page.add(
        ft.Column([
            ft.Text("📊 加班统计", size=20, weight=ft.FontWeight.BOLD),
            
            ft.Row([
                ft.Container(content=ft.Column([ft.Text("次数", size=12), total_count_text], spacing=0), expand=True, padding=10, bgcolor=ft.Colors.BLUE_50, border_radius=10),
                ft.Container(content=ft.Column([ft.Text("时长", size=12), total_hours_text], spacing=0), expand=True, padding=10, bgcolor=ft.Colors.GREEN_50, border_radius=10),
                ft.Container(content=ft.Column([ft.Text("折算", size=12), total_converted_text], spacing=0), expand=True, padding=10, bgcolor=ft.Colors.ORANGE_50, border_radius=10),
            ], spacing=8),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("➕ 添加", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([employee_dropdown, date_field], wrap=True),
                    ft.Row([hours_field, type_dropdown, ft.FilledButton("添加", icon="add", on_click=add_record_click)], wrap=True),
                ]),
                padding=10, bgcolor=ft.Colors.WHITE, border_radius=10,
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("🔍 筛选", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([filter_dropdown], wrap=True),
                    ft.Row([start_date_field, ft.Text("至"), end_date_field], wrap=True),
                    ft.Row([ft.FilledButton("查询", icon="search", on_click=apply_filter, expand=True),
                           ft.FilledButton("重置", icon="refresh", on_click=reset_filter, expand=True)]),
                ]),
                padding=10, bgcolor=ft.Colors.WHITE, border_radius=10,
            ),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("👥 员工", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([new_employee_field, ft.FilledButton("添加", icon="person_add", on_click=add_employee_click)]),
                    ft.Row([ft.FilledButton("删除员工", icon="person_remove", on_click=delete_employee_click, expand=True)]),
                ]),
                padding=10, bgcolor=ft.Colors.WHITE, border_radius=10,
            ),
            
            ft.Container(
                content=ft.Column([ft.Text("📋 记录", size=14, weight=ft.FontWeight.BOLD), records_list]),
                padding=10, bgcolor=ft.Colors.WHITE, border_radius=10,
            ),
            
            ft.Text(stats_text, size=11, color=ft.Colors.GREY_500),
        ], spacing=10)
    )
    
    refresh_data()


if __name__ == "__main__":
    ft.app(target=main)