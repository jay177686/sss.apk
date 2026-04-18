import flet as ft

def main(page: ft.Page):
    page.title = "加班统计"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    # 计数器
    count = ft.Text("0", size=50, weight=ft.FontWeight.BOLD)
    
    # 记录列表
    records = ft.Column()
    
    def add_record(e):
        # 添加记录
        current = int(count.value)
        count.value = str(current + 1)
        
        # 显示记录
        records.controls.append(
            ft.Text(f"加班记录 #{current + 1} - {__import__('datetime').datetime.now().strftime('%H:%M:%S')}")
        )
        page.update()
    
    def reset(e):
        count.value = "0"
        records.controls.clear()
        page.update()
    
    # 界面
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("员工加班统计", size=30, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("加班次数", size=20),
                count,
                ft.Row([
                    ft.ElevatedButton("+1", icon="add", on_click=add_record),
                    ft.ElevatedButton("重置", icon="refresh", on_click=reset, color=ft.Colors.RED),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Text("记录列表", size=20, weight=ft.FontWeight.BOLD),
                records,
            ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
        )
    )

ft.app(target=main)
