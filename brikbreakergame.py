import tkinter as tk
import random

# Kelas dasar untuk objek game
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas  # Canvas tempat objek berada
        self.item = item      # Objek di canvas

    def get_position(self):
        return self.canvas.coords(self.item)  # Mendapatkan koordinat objek

    def move(self, x, y):
        self.canvas.move(self.item, x, y)     # Memindahkan objek

    def delete(self):
        self.canvas.delete(self.item)         # Menghapus objek dari canvas

# Kelas untuk bola
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10                      # Radius bola
        self.direction = [1, -1]             # Arah awal bola (x, y)
        self.speed = 5                       # Kecepatan bola
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')  # Membuat bola
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()          # Posisi bola saat ini
        width = self.canvas.winfo_width()     # Lebar canvas
        if coords[0] <= 0 or coords[2] >= width:  # Pantulan dinding samping
            self.direction[0] *= -1
        if coords[1] <= 0:                    # Pantulan dinding atas
            self.direction[1] *= -1
        x = self.direction[0] * self.speed    # Pergerakan pada sumbu x
        y = self.direction[1] * self.speed    # Pergerakan pada sumbu y
        self.move(x, y)                       # Memindahkan bola

    def collide(self, game_objects):
        coords = self.get_position()          # Koordinat bola
        x = (coords[0] + coords[2]) * 0.5     # Titik tengah bola
        if len(game_objects) > 1:            # Jika ada tabrakan
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:                 # Bola ke sisi kanan paddle
                self.direction[0] = 1
            elif x < coords[0]:               # Bola ke sisi kiri paddle
                self.direction[0] = -1
            else:
                self.direction[1] *= -1       # Pantulan vertikal
        for game_object in game_objects:     # Cek tabrakan dengan brick
            if isinstance(game_object, Brick):
                game_object.hit()

# Kelas untuk paddle (dayung)
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80                       # Lebar paddle
        self.height = 10                      # Tinggi paddle
        self.ball = None                      # Bola yang terhubung
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')  # Membuat paddle
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball                      # Menghubungkan paddle ke bola

    def move(self, offset):
        coords = self.get_position()          # Posisi paddle saat ini
        width = self.canvas.winfo_width()     # Lebar canvas
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)  # Gerakkan paddle
            if self.ball is not None:          # Jika bola terhubung
                self.ball.move(offset, 0)

# Kelas untuk brick (bata)
class Brick(GameObject):
    COLORS = {1: '#FF5733', 2: '#33FF57', 3: '#3357FF'}  # Warna berdasarkan nyawa

    def __init__(self, canvas, x, y, hits):
        self.width = 75                       # Lebar brick
        self.height = 20                      # Tinggi brick
        self.hits = hits                      # Jumlah nyawa brick
        color = Brick.COLORS[hits]            # Warna brick berdasarkan nyawa
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')  # Membuat brick
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1                        # Kurangi nyawa brick
        if self.hits == 0:                    # Jika nyawa habis
            self.delete()                     # Hapus brick
            game.update_score(10)             # Tambahkan skor
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])  # Ubah warna

# Kelas untuk game
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3                        # Nyawa pemain
        self.score = 0                        # Skor awal
        self.level = 1                        # Level awal
        self.width = 610                      # Lebar canvas
        self.height = 400                     # Tinggi canvas
        self.canvas = tk.Canvas(self, bg='#123456',
                                width=self.width,
                                height=self.height)  # Membuat canvas
        self.canvas.pack()
        self.pack()

        self.items = {}                       # Menyimpan semua objek game
        self.ball = None                      # Bola dalam permainan
        self.paddle = Paddle(self.canvas, self.width / 2, 326)  # Paddle
        self.items[self.paddle.item] = self.paddle

        self.hud = None                       # Heads-up display (nyawa dan skor)
        self.score_text = None
        self.setup_game()

        self.canvas.focus_set()
        self.canvas.bind('<Left>',            # Tombol kiri untuk gerak paddle
                         lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>',           # Tombol kanan untuk gerak paddle
                         lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()                       # Tambahkan bola
        self.update_hud()                     # Perbarui HUD
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())  # Mulai game
        self.create_bricks()                  # Tambahkan brick

    def create_bricks(self):
        for x in range(5, self.width - 5, 75):  # Susun brick secara horizontal
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()                # Hapus bola lama
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)  # Tambahkan bola baru
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)  # Tambahkan brick
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)                # Font untuk teks
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_hud(self):
        lives_text = f'Lives: {self.lives}'
        score_text = f'Score: {self.score}'
        if self.hud is None:
            self.hud = self.draw_text(50, 20, lives_text, 15)  # Teks nyawa
        else:
            self.canvas.itemconfig(self.hud, text=lives_text)
        if self.score_text is None:
            self.score_text = self.draw_text(550, 20, score_text, 15)  # Teks skor
        else:
            self.canvas.itemconfig(self.score_text, text=score_text)

    def update_score(self, points):
        self.score += points                  # menambahkan skor
        self.update_hud()

    def start_game(self):
        self.canvas.unbind('<space>')         # Lepas event tombol spasi
        self.canvas.delete(self.text)        # Hapus teks awal
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()               # Periksa tabrakan
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:                   # Jika semua brick hancur
            self.ball.speed = None
            self.draw_text(300, 200, 'You Win!')
        elif self.ball.get_position()[3] >= self.height:  # Bola jatuh
            self.lives -= 1
            if self.lives == 0:               # Nyawa habis
                self.draw_text(300, 200, 'Game Over')
            else:
                self.add_ball()
        else:
            self.ball.update()               # Perbarui posisi bola
            self.after(50, self.game_loop)   # Loop setiap 50ms

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)  # Cek tabrakan
        game_objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(game_objects)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Brick Breaker')
    game = Game(root)
    game.mainloop()
