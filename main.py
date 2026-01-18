from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.utils import platform
import sqlite3

# ===== ANDROID =====
if platform == "android":
    from jnius import autoclass
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
    activity = PythonActivity.mActivity
    vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

# ===== CARTAS FOOTBALL =====
FOOTBALL_CARTAS = [
    (2, "2"), (3, "3"), (4, "4"), (5, "5"), (6, "6"),
    (7, "7"), (8, "8"), (9, "9"), (10, "10"),
    (11, "J"), (12, "Q"), (13, "K"), (14, "A")
]

CARTA_TEXTO = {11: "J", 12: "Q", 13: "K", 14: "A"}

class BacBoCatalogador(App):

    def build(self):
        self.conectar_db()

        self.azul = None
        self.vermelho = None
        self.modo_visualizacao = "Nb"
        self.menu_visivel = False
        self.jogo_atual = "BACBO"

        self.root_layout = BoxLayout(orientation="vertical", padding=5, spacing=5)

        # ===== HISTÓRICO =====
        self.scroll = ScrollView(size_hint=(1, None), height=600,
                                 do_scroll_x=True, do_scroll_y=False)

        self.historico_layout = BoxLayout(
            orientation="horizontal",
            size_hint_x=None,
            spacing=2,
            padding=5
        )
        self.historico_layout.bind(
            minimum_width=self.historico_layout.setter("width")
        )

        self.scroll.add_widget(self.historico_layout)
        self.root_layout.add_widget(self.scroll)
        self.root_layout.add_widget(Widget(size_hint_y=None, height=50))

        # ===== BOTÕES =====
        self.azul_layout = BoxLayout(size_hint=(1, None), height=100, spacing=2)
        self.vermelho_layout = BoxLayout(size_hint=(1, None), height=100, spacing=2)

        self.root_layout.add_widget(self.azul_layout)
        self.root_layout.add_widget(self.vermelho_layout)

        # ===== MENU =====
        btn_menu = Button(text="MENU", size_hint=(1, None), height=100)
        btn_menu.bind(on_press=self.toggle_menu)
        self.root_layout.add_widget(btn_menu)

        self.menu_layout = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=130,
            spacing=5,
            opacity=0,
            disabled=True
        )

        btn_limpar = Button(text="Limpar Histórico")
        btn_limpar.bind(on_press=self.limpar_historico)

        btn_desfazer = Button(text="Desfazer Última")
        btn_desfazer.bind(on_press=self.desfazer_ultima)

        self.btn_modo = Button(text="VER: Nb / NA")
        self.btn_modo.bind(on_press=self.alternar_modo)

        self.btn_jogo = Button(text="JOGO: BACBO")
        self.btn_jogo.bind(on_press=self.trocar_jogo)

        self.menu_layout.add_widget(btn_limpar)
        self.menu_layout.add_widget(btn_desfazer)
        self.menu_layout.add_widget(self.btn_modo)
        self.menu_layout.add_widget(self.btn_jogo)

        self.root_layout.add_widget(self.menu_layout)

        self.criar_botoes()
        self.carregar_historico()
        return self.root_layout

    # ===== BANCO =====
    def conectar_db(self):
        self.conn = sqlite3.connect("bacbo.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                azul INTEGER,
                vermelho INTEGER,
                jogo TEXT
            )
        """)
        self.conn.commit()

    # ===== BOTÕES =====
    def criar_botoes(self):
        self.azul_layout.clear_widgets()
        self.vermelho_layout.clear_widgets()

        valores = [(n, str(n)) for n in range(2, 13)] if self.jogo_atual == "BACBO" else FOOTBALL_CARTAS

        for valor, texto in valores:
            btn_azul = Button(text=texto, font_size=30, bold=True,
                              background_color=(0.2, 0.4, 1, 1))
            btn_azul.bind(on_press=lambda x, v=valor: self.selecionar_azul(v))
            self.azul_layout.add_widget(btn_azul)

            btn_vermelho = Button(text=texto, font_size=30, bold=True,
                                  background_color=(1, 0.2, 0.2, 1))
            btn_vermelho.bind(on_press=lambda x, v=valor: self.selecionar_vermelho(v))
            self.vermelho_layout.add_widget(btn_vermelho)

    # ===== MENU =====
    def toggle_menu(self, *_):
        self.menu_visivel = not self.menu_visivel
        self.menu_layout.opacity = 1 if self.menu_visivel else 0
        self.menu_layout.disabled = not self.menu_visivel

    def trocar_jogo(self, *_):
        self.jogo_atual = "FOOTBALL" if self.jogo_atual == "BACBO" else "BACBO"
        self.btn_jogo.text = f"JOGO: {self.jogo_atual}"

        if self.jogo_atual == "FOOTBALL":
            self.btn_modo.text = "VER: CLASSES" if self.modo_visualizacao == "Nb" else "VER: CARTAS"
        else:
            self.btn_modo.text = "VER: Nb / NA" if self.modo_visualizacao == "Nb" else "VER: NÚMEROS"

        self.criar_botoes()
        self.carregar_historico()

    # ===== VIBRAÇÃO =====
    def vibrar(self):
        if platform == "android":
            vibrator.vibrate(40)

    # ===== SELEÇÃO =====
    def selecionar_azul(self, v):
        self.vibrar()
        self.azul = v
        self.verificar()

    def selecionar_vermelho(self, v):
        self.vibrar()
        self.vermelho = v
        self.verificar()

    def verificar(self):
        if self.azul is not None and self.vermelho is not None:
            self.salvar(self.azul, self.vermelho)
            self.azul = None
            self.vermelho = None

    # ===== SALVAR =====
    def salvar(self, azul, vermelho):
        self.cursor.execute(
            "INSERT INTO historico (azul, vermelho, jogo) VALUES (?, ?, ?)",
            (azul, vermelho, self.jogo_atual)
        )
        self.conn.commit()
        self.carregar_historico()

    # ===== DESFAZER =====
    def desfazer_ultima(self, *_):
        self.cursor.execute(
            "DELETE FROM historico WHERE id = (SELECT MAX(id) FROM historico WHERE jogo = ?)",
            (self.jogo_atual,)
        )
        self.conn.commit()
        self.carregar_historico()

    # ===== CLASSIFICAÇÕES =====
    def classificar_bacbo(self, v):
        if v in [3,4,5,6]: return "Nb"
        if v in [8,9,10,11]: return "NA"
        if v == 7: return "N"
        return str(v)

    def classificar_football(self, v):
        if v in [4,5,6,7]: return "Nb"
        if v in [9,10]: return "NA"
        if v in [11,12,13]: return "L"
        if v == 8: return "N"
        return CARTA_TEXTO.get(v, str(v))

    # ===== MODO VISUAL =====
    def alternar_modo(self, btn):
        self.modo_visualizacao = "NUM" if self.modo_visualizacao == "Nb" else "Nb"

        if self.jogo_atual == "FOOTBALL":
            btn.text = "VER: CARTAS" if self.modo_visualizacao == "NUM" else "VER: CLASSES"
        else:
            btn.text = "VER: NÚMEROS" if self.modo_visualizacao == "NUM" else "VER: Nb / NA"

        self.carregar_historico()

    # ===== HISTÓRICO (CORRIGIDO) =====
    def carregar_historico(self):
        self.historico_layout.clear_widgets()
        self.cursor.execute(
            "SELECT azul, vermelho FROM historico WHERE jogo = ? ORDER BY id DESC",
            (self.jogo_atual,)
        )

        for azul, vermelho in self.cursor.fetchall():
            maior, menor = (azul, vermelho) if azul >= vermelho else (vermelho, azul)

            if self.modo_visualizacao == "NUM":
                if self.jogo_atual == "FOOTBALL":
                    texto = f"{CARTA_TEXTO.get(maior, maior)}\nX\n{CARTA_TEXTO.get(menor, menor)}"
                else:
                    texto = f"{maior}\nX\n{menor}"
            else:
                if self.jogo_atual == "FOOTBALL":
                    texto = f"{self.classificar_football(maior)}\nX\n{self.classificar_football(menor)}"
                else:
                    texto = f"{self.classificar_bacbo(maior)}\nX\n{self.classificar_bacbo(menor)}"

            cor = (
                (1,0.95,0.3,1) if azul == vermelho else
                (0.25,0.5,1,1) if azul > vermelho else
                (1,0.3,0.3,1)
            )

            self.historico_layout.add_widget(
                Button(text=texto, size_hint=(None,None),
                       width=60, height=95,
                       font_size=18, bold=True,
                       background_color=cor)
            )

    # ===== LIMPAR =====
    def limpar_historico(self, *_):
        self.cursor.execute(
            "DELETE FROM historico WHERE jogo = ?",
            (self.jogo_atual,)
        )
        self.conn.commit()
        self.carregar_historico()


if __name__ == "__main__":
    BacBoCatalogador().run()
