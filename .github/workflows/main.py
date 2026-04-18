import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "加班统计系统"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # 存储加班记录
    records = []
    
    # 输入控件
    employee_name = ft.TextField(label="员工姓名", width=200)
    hours = ft.TextField(label="加班时长(小时)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
    date = ft.TextField(label="日期", value=datetime.now().strftime("%Y-%m-%d"), width=150)
    
    # 统计显示
    total_count = ft.Text("0", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600)
    total_hours = ft.Text("0", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
    
    # 记录列表
    records_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=400)
    
    def refresh_display():
        # 更新统计
        total_count.value = str(len(records))
        total_hours.value = f"{sum(r['hours'] for r in records):.1f}"
        
        # 更新列表
        records_list.controls.clear()
        for i, record in enumerate(reversed(records)):
            records_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"{record['employee']} - {record['date']}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"加班时长: {record['hours']}小时"),
                        ]),
                        padding=10,
                    )
                )
            )
        page.update()
    
    def add_record(e):
        if not employee_name.value:
            page.snack_bar = ft.SnackBar(content=ft.Text("请输入员工姓名"))
            page.snack_bar.open = True
            page.update()
            return
        
        try:
            h = float(hours.value) if hours.value else 0
            if h <= 0:
                raise ValueError
        except ValueError:
            page.snack_bar = ft.SnackBar(content=ft.Text("请输入有效的加班时长"))
            page.snack_bar.open = True
            page.update()
            return
        
        records.append({
            "employee": employee_name.value,
            "hours": h,
            "date": date.value
        })
        
        employee_name.value = ""
        hours.value = ""
        
        refresh_display()
        
        page.snack_bar = ft.SnackBar(content=ft.Text("添加成功"), bgcolor=ft.Colors.GREEN_600)
        page.snack_bar.open = True
        page.update()
    
    def clear_records(e):
        records.clear()
        refresh_display()
        page.snack_bar = ft.SnackBar(content=ft.Text("已清空所有记录"))
        page.snack_bar.open = True
        page.update()
    
    # 布局
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("员工加班统计系统", size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("统计信息", size=18, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Column([ft.Text("总加班次数", size=14), total_count], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.VerticalDivider(),
                                ft.Column([ft.Text("总加班时长", size=14), total_hours], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                        ]),
                        padding=15,
                    )
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("添加加班记录", size=18, weight=ft.FontWeight.BOLD),
                            employee_name,
                            hours,
                            date,
                            ft.Row([
                                ft.ElevatedButton("添加", icon="add", on_click=add_record),
                                ft.ElevatedButton("清空", icon="delete", on_click=clear_records, color=ft.Colors.RED),
                            ], alignment=ft.MainAxisAlignment.END),
                        ]),
                        padding=15,
                    )
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("加班记录列表", size=18, weight=ft.FontWeight.BOLD),
                            records_list,
                        ]),
                        padding=15,
                    )
                ),
            ], spacing=15),
            padding=10,
        )
    )

ft.app(target=main)
