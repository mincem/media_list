class ColorPicker:
    COLORS = [
        '#dc3545', '#dd3844', '#dd3b43', '#de3d41', '#df4040', '#e0433f', '#e0463e', '#e1493c', '#e24b3b', '#e24e3a',
        '#e35139', '#e45437', '#e45736', '#e55935', '#e65c34', '#e75f32', '#e76231', '#e86530', '#e9672f', '#e96a2d',
        '#ea6d2c', '#eb702b', '#eb732a', '#ec7528', '#ed7827', '#ee7b26', '#ee7e25', '#ef8124', '#f08322', '#f08621',
        '#f18920', '#f28c1f', '#f28f1d', '#f3911c', '#f4941b', '#f5971a', '#f59a18', '#f69d17', '#f79f16', '#f7a215',
        '#f8a513', '#f9a812', '#f9ab11', '#faad10', '#fbb00e', '#fcb30d', '#fcb60c', '#fdb90b', '#febb09', '#febe08',
        '#ffc107', '#fbc008', '#f6c009', '#f2bf0b', '#eebf0c', '#e9be0d', '#e5be0e', '#e1bd10', '#ddbd11', '#d8bc12',
        '#d4bc13', '#d0bb15', '#cbbb16', '#c7ba17', '#c3ba18', '#bfb91a', '#bab91b', '#b6b81c', '#b2b81d', '#adb71f',
        '#a9b720', '#a5b621', '#a0b622', '#9cb524', '#98b525', '#94b426', '#8fb327', '#8bb328', '#87b22a', '#82b22b',
        '#7eb12c', '#7ab12d', '#75b02f', '#71b030', '#6daf31', '#69af32', '#64ae34', '#60ae35', '#5cad36', '#57ad37',
        '#53ac39', '#4fac3a', '#4aab3b', '#46ab3c', '#42aa3e', '#3eaa3f', '#39a940', '#35a941', '#31a843', '#2ca844',
        '#28a745'
    ]

    def color_for(self, value):
        try:
            return self.COLORS[value]
        except IndexError:
            return '#000000'
