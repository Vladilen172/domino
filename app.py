from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
import sys
import design
import random


class Domino:
    def __init__(self, left, right):
        """
        Инициализируем класс Domino с левым и правым значениями.
        """
        self.left = left
        self.right = right

    def __str__(self):
        """
        Возвращает строковый вид класса Domino в формате "[left|right]".
        """
        return f"[{self.left} | {self.right}]"


class App(design.Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.dominoes = [Domino(i, j) for i in range(7) for j in range(i, 7)]
        self.board = []
        self.player_hand = []
        self.computer_hand = []
        self.deal_dominoes()
        self.display_board_print()
        self.addDomino.clicked.connect(self.add_domino_gamer)
        self.start.clicked.connect(self.play)
        self.restart.clicked.connect(self.restart_game)
        self.right.setChecked(True)

    def draw_domino(self):
        """
        Вытягивает случайную кость домино из набора оставшихся костей.
        Возвращает нарисованное домино.
        """
        return self.dominoes.pop(random.randint(0, len(self.dominoes) - 1))

    def deal_dominoes(self):
        """
        Метод сдает 7 домино игроку и 7 домино компьютеру.
        """
        for _ in range(7):
            self.player_hand.append(self.draw_domino())
            self.computer_hand.append(self.draw_domino())

    def add_domino_gamer(self):
        """
        Метод добавляет домино игроку, если домино не хватает.
        """
        if len(self.dominoes) == 0:
            QMessageBox.about(self, "Предупреждение", "В колоде закончились домино.")
            return

        if len(self.player_hand) == 9:
            QMessageBox.about(self, "Предупреждение", "У вас могут быть только девять домино на руках.")
            return

        if len(self.board) == 0:
            QMessageBox.about(self, "Предупреждение", "Пока вы не поставите домино на стол, вы не можете брать из колоды")
            return

        new_domino = self.draw_domino()
        if new_domino is not None:
            self.player_hand.append(new_domino)
            self.display_board_print()
            self.addDomino.setText(str(len(self.dominoes)))
            self.replace_domino()
            self.refery.addItem(f"Игрок взял: {new_domino}")
            self.logic_computer()

        self.display_board_print()
        self.replace_domino()
        self.show_domino()
        self.countDominoComputer.setText(f"У компьютера осталось {len(self.computer_hand)} домино")

    def display_board_print(self):
        """
        Отображение текущего состояния игры, включая поле, руку игрока и руку компьютера.
        """
        print("Оставшиеся домино: ", " ".join(map(str, self.dominoes)))
        print("Стол:", " ".join(map(str, self.board)))
        print("Мои кости:", " ".join(map(str, self.player_hand)))
        print("Кости компьютера:", " ".join(map(str, self.computer_hand)))

    def logic_computer(self):
        if any(domino.left in (self.board[0].left, self.board[-1].right) or domino.right in (self.board[0].left, self.board[-1].right) for domino in self.computer_hand):
            while True:
                computer_move = random.randint(0, len(self.computer_hand) - 1)
                domino_to_play = self.computer_hand.pop(computer_move)
                if domino_to_play.left in (self.board[0].left, self.board[-1].right) or domino_to_play.right in (self.board[0].left, self.board[-1].right):
                    self.process_domino_computer(domino_to_play)
                    self.refery.addItem(f"Компьютер пошел: {domino_to_play}")
                    break
                else:
                    self.computer_hand.append(domino_to_play)
        else:
            if len(self.dominoes) == 0:
                QMessageBox.about(self, "Вы победили", "У компьютера закончились доступные домино.")
                self.restart_game()
                return

            new_domino = self.draw_domino()
            if new_domino:
                self.computer_hand.append(new_domino)
                self.refery.addItem(f"Компьютер взял: [? | ?]")
        self.addDomino.setText(str(len(self.dominoes)))

    def process_domino_gamer(self, domino):
        """
        Проверяет, что домино можно поставить на доску так, чтобы число совпадало с краем уже существующего домино,
        учитывая выбор сторон. При необходимости переворачивает домино.

        Аргументы:
            domino: Домино, которое нужно проверить и, при необходимости, перевернуть.
        """
        if not self.board:
            # Если доска пуста, добавляем домино на доску.
            self.board.append(domino)
            self.refery.addItem(f"Игрок пошел: {domino}")
            return

        # левый и правые края доски
        left_edge = self.board[0].left
        right_edge = self.board[-1].right

        if self.right.isChecked():
            # Если число слева совпадает с правым краем доски, добавляем домино в конец доски.
            if domino.left == right_edge:
                self.board.append(domino)
                self.refery.addItem(f"Игрок пошел: {domino}")

            # Если число справа совпадает с левым краем доски, добавляем перевернутое домино в конец доски.
            elif domino.right == right_edge:
                self.board.append(Domino(domino.right, domino.left))
                self.refery.addItem(f"Игрок пошел: {domino}")

            # Если домино не соприкасается с краями доски, добавляем его в руку игрока.
            else:
                self.player_hand.append(domino)
                self.refery.addItem("Игрок выбрал не то домино. \nШтраф: пропуск хода.")

        if self.left.isChecked():
            # Если число слева совпадает с левым краем доски, добавляем домино в начало доски.
            if domino.left == left_edge:
                self.board.insert(0, Domino(domino.right, domino.left))
                self.refery.addItem(f"Игрок пошел: {domino}")

            # Если число справа совпадает с правым краем доски, добавляем перевернутое домино в начало доски.
            elif domino.right == left_edge:
                self.board.insert(0, domino)
                self.refery.addItem(f"Игрок пошел: {domino}")

            # Если домино не соприкасается с краями доски, добавляем его в руку игрока.
            else:
                self.player_hand.append(domino)
                self.refery.addItem("Игрок выбрал не то домино. \nШтраф: пропуск хода.")

        self.check_draw()

    def process_domino_computer(self, domino):
        """
        Проверяет, что домино можно поставить на доску так, чтобы число совпадало с краем уже существующего домино.
        При необходимости переворачивает домино.

        Аргументы:
            domino: Домино, которое нужно проверить и, при необходимости, перевернуть.
        """

        # левый и правые края доски
        left_edge = self.board[0].left
        right_edge = self.board[-1].right

        # Если число слева совпадает с левым краем доски, добавляем домино в начало доски.
        if domino.left == left_edge:
            self.board.insert(0, Domino(domino.right, domino.left))

        # Если число слева совпадает с правым краем доски, добавляем домино в конец доски.
        elif domino.left == right_edge:
            self.board.append(domino)

        # Если число справа совпадает с правым краем доски, добавляем перевернутое домино в начало доски.
        elif domino.right == left_edge:
            self.board.insert(0, domino)

        # Если число справа совпадает с левым краем доски, добавляем перевернутое домино в конец доски.
        elif domino.right == right_edge:
            self.board.append(Domino(domino.right, domino.left))

        # Если домино не соприкасается с краями доски, добавляем его в руку игрока.
        else:
            self.player_hand.append(domino)

        if len(self.computer_hand) == 0:
            QMessageBox.about(self, "Очень жаль : (", "Вы проиграли. Компьютер избавился от домино раньше вас.\nЗа покупку premium подписки или за зачет по программированию с тестированием открывается возможность видеть домино противника.")
            self.restart_game()
            return

        self.check_draw()

    def restart_game(self):
        """
            Обнуляем все значения и начинаем игру заново
        """
        self.board = []
        self.player_hand = []
        self.computer_hand = []
        self.dominoes = [Domino(i, j) for i in range(7) for j in range(i, 7)]
        self.deal_dominoes()
        self.display_board_print()
        self.replace_domino()
        self.addDomino.setText(str(len(self.dominoes)))
        self.countDominoComputer.setText(f"У компьютера осталось {len(self.computer_hand)} домино")
        self.refery.clear()
        self.hide_domino()

    def play(self):
        """
            Игра продолжается до тех пор, пока у игрока или компьютера не закончатся костяшки домино.
        """
        self.replace_domino()
        # ход игрока
        player_move = int(self.spinBox.value()) - 1
        if player_move < 0 or player_move >= len(self.player_hand):
            self.refery.addItem(f"Игрок выбрал несуществующее домино. \nШтраф: пропуск хода.")

        else:
            domino_to_play = self.player_hand.pop(player_move)
            self.process_domino_gamer(domino_to_play)

        if len(self.player_hand) == 0:
            QMessageBox.about(self, "Поздравляем : )", "Вы победили!!!\nЗа покупку premium подписки или за зачет по программированию открывается возможность видеть домино противника.")
            self.restart_game()
            return

        # ход компьютера
        self.logic_computer()
        self.display_board_print()
        self.replace_domino()
        self.countDominoComputer.setText(f"У компьютера осталось {len(self.computer_hand)} домино")
        self.show_domino()

    def replace_domino(self):
        """
            Выводим наши домино в графический интерфейс и ненужные домино прячем с помощью метода hide()
        """
        domino_widgets_gamer = [self.domino1, self.domino2, self.domino3, self.domino4, self.domino5, self.domino6, self.domino7, self.domino8, self.domino9]
        domino_widgets_computer = [self.domino_1, self.domino_2, self.domino_3, self.domino_4, self.domino_5, self.domino_6, self.domino_7, self.domino_8, self.domino_9]

        for i in range(9, 0, -1):
            if len(self.player_hand) >= i:
                domino_widgets_gamer[i - 1].show()
            else:
                domino_widgets_gamer[i - 1].hide()

        for i in range(9, 0, -1):
            if len(self.computer_hand) >= i:
                domino_widgets_computer[i - 1].show()
            else:
                domino_widgets_computer[i - 1].hide()

        for i in range(len(self.player_hand)):
            domino_widgets_gamer[i].setText(str(self.player_hand[i]).replace("[", '').replace(" ", "\n").replace("|", "---").replace("]", ''))

        for i in range(len(self.player_hand), len(domino_widgets_gamer)):
            domino_widgets_gamer[i].setText("")

    def check_draw(self):
        """
        Проверяет, возможен ли ход какому-либо игроку.
        Если ни у игрока, ни у компьютера нет возможности походить, то игра заканчивается в ничью.
        """
        if int(self.addDomino.text()) == 0:
            if not any(domino.left in (self.board[0].left, self.board[-1].right) or domino.right in (self.board[0].left, self.board[-1].right) for domino in self.player_hand):
                if not any(domino.left in (self.board[0].left, self.board[-1].right) or domino.right in (self.board[0].left, self.board[-1].right) for domino in self.computer_hand):
                    QMessageBox.about(self, "Ничья", "В игре наступила ничья. Кончились возможные ходы для обоих игроков.")
                    self.restart_game()

            elif not any(domino.left in (self.board[0].left, self.board[-1].right) or domino.right in (self.board[0].left, self.board[-1].right) for domino in self.player_hand):
                QMessageBox.about(self, "Вы проиграли", "У вас закончились допустимые домино.")
                self.restart_game()
            elif not any(domino.left in (self.board[0].left, self.board[-1].right) or domino.right in (self.board[0].left, self.board[-1].right) for domino in self.computer_hand):
                QMessageBox.about(self, "Вы победили", "У компьютера закончились допустимые домино.")
                self.restart_game()

        else:
            return

    def hide_domino(self):
        """
            Метод прячет все кости домино на доске.
        """
        tableDomino = [self.dom, self.dom_2, self.dom_3, self.dom_4, self.dom_5, self.dom_6, self.dom_7, self.dom_8,
                       self.dom_9, self.dom_10, self.dom_11, self.dom_12, self.dom_13, self.dom_14, self.dom_15,
                       self.dom_16, self.dom_17, self.dom_18, self.dom_19]

        for i in range(0, 19):
            tableDomino[i].hide()

    def del_domino(self):
        """
            Метод удаляет 10 домино в середине, если домино равно 19 или больше. На результат игры не влияет.
        """
        if len(self.board) >= 19:
            del self.board[6:15]
            self.dom_19.hide()
            self.dom_17.hide()
            self.dom_15.hide()
            self.dom_13.hide()
            self.dom_11.hide()
            self.dom_10.hide()
            self.dom_12.hide()
            self.dom_14.hide()
            self.dom_16.hide()
            self.dom_18.hide()
            self.refery.addItem(f"Домино в середине исчезли \nиз-за ненадобности.")

    def show_domino(self):
        """
            Метод делает видимыми домино на столе, учитывая длину ряда домино
        """
        self.del_domino()

        if len(self.board) == 0:
            return

        elif len(self.board) == 1:
            self.dom.show()
            self.dom.setText(map(str, self.board[0]))

        elif len(self.board) == 2:
            self.dom.show()
            self.dom_2.show()
            self.dom.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 3:
            self.dom.show()
            self.dom_2.show()
            self.dom_3.show()
            self.dom_3.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 4:
            self.dom_3.show()
            self.dom_4.show()
            self.dom_3.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 5:
            self.dom_4.show()
            self.dom_5.show()
            self.dom_5.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 6:
            self.dom_5.show()
            self.dom_6.show()
            self.dom_5.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 7:
            self.dom_6.show()
            self.dom_7.show()
            self.dom_7.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 8:
            self.dom_7.show()
            self.dom_8.show()
            self.dom_7.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 9:
            self.dom_8.show()
            self.dom_9.show()
            self.dom_9.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 10:
            self.dom_9.show()
            self.dom_10.show()
            self.dom_9.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 11:
            self.dom_10.show()
            self.dom_11.show()
            self.dom_11.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 12:
            self.dom_11.show()
            self.dom_12.show()
            self.dom_11.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 13:
            self.dom_12.show()
            self.dom_13.show()
            self.dom_13.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 14:
            self.dom_13.show()
            self.dom_14.show()
            self.dom_13.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))
            self.dom_14.setText(str(self.board[13]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 15:
            self.dom_14.show()
            self.dom_15.show()
            self.dom_15.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_13.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[13]).replace('[', ' ').replace(']', ' '))
            self.dom_14.setText(str(self.board[14]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 16:
            self.dom_15.show()
            self.dom_16.show()
            self.dom_15.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_13.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[13]).replace('[', ' ').replace(']', ' '))
            self.dom_14.setText(str(self.board[14]).replace('[', ' ').replace(']', ' '))
            self.dom_16.setText(str(self.board[15]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 17:
            self.dom_16.show()
            self.dom_17.show()
            self.dom_17.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_15.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_13.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[13]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[14]).replace('[', ' ').replace(']', ' '))
            self.dom_14.setText(str(self.board[15]).replace('[', ' ').replace(']', ' '))
            self.dom_16.setText(str(self.board[16]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 18:
            self.dom_17.show()
            self.dom_18.show()
            self.dom_17.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_15.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_13.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[13]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[14]).replace('[', ' ').replace(']', ' '))
            self.dom_14.setText(str(self.board[15]).replace('[', ' ').replace(']', ' '))
            self.dom_16.setText(str(self.board[16]).replace('[', ' ').replace(']', ' '))
            self.dom_18.setText(str(self.board[17]).replace('[', ' ').replace(']', ' '))

        elif len(self.board) == 19:
            self.dom_18.show()
            self.dom_19.show()
            self.dom_19.setText(str(self.board[0]).replace('[', ' ').replace(']', ' '))
            self.dom_17.setText(str(self.board[1]).replace('[', ' ').replace(']', ' '))
            self.dom_15.setText(str(self.board[2]).replace('[', ' ').replace(']', ' '))
            self.dom_13.setText(str(self.board[3]).replace('[', ' ').replace(']', ' '))
            self.dom_11.setText(str(self.board[4]).replace('[', ' ').replace(']', ' '))
            self.dom_9.setText(str(self.board[5]).replace('[', ' ').replace(']', ' '))
            self.dom_7.setText(str(self.board[6]).replace('[', ' ').replace(']', ' '))
            self.dom_5.setText(str(self.board[7]).replace('[', ' ').replace(']', ' '))
            self.dom_3.setText(str(self.board[8]).replace('[', ' ').replace(']', ' '))
            self.dom.setText(str(self.board[9]).replace('[', ' ').replace(']', ' '))
            self.dom_2.setText(str(self.board[10]).replace('[', ' ').replace(']', ' '))
            self.dom_4.setText(str(self.board[11]).replace('[', ' ').replace(']', ' '))
            self.dom_6.setText(str(self.board[12]).replace('[', ' ').replace(']', ' '))
            self.dom_8.setText(str(self.board[13]).replace('[', ' ').replace(']', ' '))
            self.dom_10.setText(str(self.board[14]).replace('[', ' ').replace(']', ' '))
            self.dom_12.setText(str(self.board[15]).replace('[', ' ').replace(']', ' '))
            self.dom_14.setText(str(self.board[16]).replace('[', ' ').replace(']', ' '))
            self.dom_16.setText(str(self.board[17]).replace('[', ' ').replace(']', ' '))
            self.dom_18.setText(str(self.board[18]).replace('[', ' ').replace(']', ' '))


def main():
    app = QApplication(sys.argv)
    window = App()
    window.replace_domino()
    window.hide_domino()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
