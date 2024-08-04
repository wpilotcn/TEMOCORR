import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, BOTTOM

def coldICAO(Elevation, Hthr, Hfix, Dh):
    import math
    ISA = 15  # 摄氏度
    Lo = -0.0065  # 摄氏度/米
    To = 288.15  # K
    Tisa = ISA + Lo * Elevation
    Tdiff = (-Dh * Lo) / math.log(1 + Lo * Hfix / (To + Lo * Hthr))
    Temp = Tisa + Tdiff
    return Temp

class ColdThresholdCalculator(toga.App):

    def startup(self):
        # 创建主窗口并设置宽度
        self.main_window = toga.MainWindow(title=self.formal_name, size=(375, 580))

        # 创建输入框和按钮
        self.elevation_label = toga.Label('机场标高 (米):   ', style=Pack(padding=(3, 5), color='#006001'))
        self.elevation_input = toga.TextInput(placeholder='输入机场标高，单位(米)', style=Pack(width=245))

        self.hthr_label = toga.Label('入口标高 (米):   ', style=Pack(padding=(3, 5), color='#006001'))
        self.hthr_input = toga.TextInput(placeholder='输入跑道入口标高，单位(米)', style=Pack(width=245))

        self.hfix_label = toga.Label('修正点真高 (米):', style=Pack(padding=(3, 5), color='#006001'))
        self.hfix_input = toga.TextInput(placeholder='输入修正点真高，单位(米)', style=Pack(width=245))

        self.program_label = toga.Label('程序高度 (米):   ', style=Pack(padding=(3, 5), color='#006001'))
        self.program_input = toga.TextInput(placeholder='输入程序高度，单位(米)', style=Pack(width=245))

        self.moca_label = toga.Label('MOCA高度 (米):', style=Pack(padding=(5, 5), color='#006001'))
        self.moca_input = toga.TextInput(placeholder='输入MOCA高度，单位(米)', style=Pack(width=245))

        self.mid_label = toga.Label(' 选择进近阶段:   ', style=Pack(padding_right=3, color='#0000FF'))
        self.choice_box = toga.Selection(items=['起 始 进 近 段', '中 间 进 近 段', '最 后 进 近 段'], on_change=self.on_choice_select, style=Pack(width=246, padding=(0, 3), color='#0000FF'))

        self.result_label = toga.Label('', style=Pack(color='blue'))
        self.moc_label = toga.Label('', style=Pack(color='green'))

        calc_button = toga.Button('计 算', on_press=self.calculate, style=Pack(padding=(5, 5), color='#006001'))
        reset_button = toga.Button('重 置', on_press=self.reset, style=Pack(padding=(5, 5), color='#006001'))

        # 添加顶部提示文本
        self.top_label = toga.Label(
            '                    ☆ 低 温 修 正 阈 值 计 算 器 ☆\n                                                            -- By 王 鹏 \n-------------------------------------------------------------',
            style=Pack(padding_bottom=10, color='#008000')  # 使用颜色代码设置绿色
        )

        # 添加底部版权文本
        self.bottom_label = toga.Label(
            '版权所有 © 2024 wpilot \nBUG报告：wpilotcn@gmail.com \n人一能之，己百之；人十能之，己千之；\n果能此道矣，虽愚必明，虽柔必强。  --《博学之》',
            style=Pack(padding=(5, 0, 0, 5), color='#008000', flex=1, alignment=BOTTOM)
        )

        # 布局
        input_box = toga.Box(
            children=[
                self.top_label,
                toga.Box(children=[self.elevation_label, self.elevation_input], style=Pack(direction=ROW, padding=5)),
                toga.Box(children=[self.hthr_label, self.hthr_input], style=Pack(direction=ROW, padding=5)),
                toga.Box(children=[self.hfix_label, self.hfix_input], style=Pack(direction=ROW, padding=5)),
                toga.Box(children=[self.mid_label, self.choice_box], style=Pack(direction=ROW, padding=5)),
                toga.Box(children=[self.program_label, self.program_input], style=Pack(direction=ROW, padding=5)),
                toga.Box(children=[self.moca_label, self.moca_input], style=Pack(direction=ROW, padding=5)),
                calc_button,
                reset_button,
                self.moc_label,
                self.result_label,
            ],
            style=Pack(direction=COLUMN, padding=10, padding_top=5, padding_bottom=5)
        )

        # 使用ScrollContainer包装input_box
        scroll_container = toga.ScrollContainer(content=input_box, style=Pack(flex=1))

        # 创建主容器
        main_box = toga.Box(
            children=[
                scroll_container,
                self.bottom_label,  # 添加底部版权文本到主容器中
            ],
            style=Pack(direction=COLUMN, flex=1)
        )

        self.main_window.content = main_box
        self.main_window.show()

    def on_choice_select(self, widget):
        choice = self.choice_box.value
        if choice == '最 后 进 近 段':
            self.program_input.enabled = False
            self.moca_input.enabled = False
        else:
            self.program_input.enabled = True
            self.moca_input.enabled = True

    def calculate(self, widget):
        try:
            Elevation = float(self.elevation_input.value)
            Hthr = float(self.hthr_input.value)
            Hfix = int(self.hfix_input.value)

            choice = self.choice_box.value
            if choice == '起 始 进 近 段':
                moc = 300
                program = int(self.program_input.value)
                moca = int(self.moca_input.value)
                h1 = program - moca
                h2 = 0.2 * moc
                Dh = h1 + h2
            elif choice == '中 间 进 近 段':
                moc = 150
                program = int(self.program_input.value)
                moca = int(self.moca_input.value)
                h1 = program - moca
                h2 = 0.2 * moc
                Dh = h1 + h2
            elif choice == '最 后 进 近 段':
                moc = 75
                Dh = 0.2 * moc
            else:
                self.result_label.text = "选择错误"
                return

            self.moc_label.text = f"\nMOC值为: {moc} 米"

            Temp = coldICAO(Elevation, Hthr, Hfix, Dh)
            T = int(Temp)
            self.result_label.text = f"\n门限温度为: {Temp:.2f} ℃\n向上取整门限温度为: [{T} ℃]"
           
        except ValueError:
            self.result_label.text = "\n输入无效，请输入有效的数字"

    def reset(self, widget):
        self.elevation_input.value = ''
        self.hthr_input.value = ''
        self.hfix_input.value = ''
        self.program_input.value = ''
        self.moca_input.value = ''
        self.choice_box.value = None
        self.result_label.text = ''
        self.moc_label.text = ''

def main():
    return ColdThresholdCalculator(icon='resources/airplane.ico')

if __name__ == '__main__':
    main().main_loop()
