import flet as ft
import asyncio
import aiohttp

pokemon_actual = 0


async def main(page: ft.Page):
    ## Inicializamos la ventana
    page.window_width = 390
    page.window_height = 800
    page.window_resizable = False
    page.padding = 0
    page.margin = 0
    page.fonts = {
        "zpix": "https://github.com/SolidZORO/zpix-pixel-font/releases/download/v3.1.8/zpix.ttf"
    }
    page.theme = ft.Theme(font_family="zpix")

    ## Funciones del programa:
    async def peticion(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    async def evento_get_pokemon(e: ft.ContainerTapEvent):
        global pokemon_actual
        if e.control == flecha_superior:
            pokemon_actual += 1
        else:
            pokemon_actual -= 1
        numero = (pokemon_actual % 151) + 1
        await actualizar_pokemon(numero)

    async def actualizar_pokemon(numero):
        resultado = await peticion(f"https://pokeapi.co/api/v2/pokemon/{numero}")
        species_info = await peticion(resultado["species"]["url"])

        # Obtener la descripción en español
        descripcion_esp = next(
            (
                entry["flavor_text"]
                for entry in species_info["flavor_text_entries"]
                if entry["language"]["name"] == "es"
            ),
            "Descripción no disponible en español.",
        )

        # Obtener los ataques (limitado a 4 más comunes)
        ataques = []
        for move in resultado["moves"][:4]:
            move_info = await peticion(move["move"]["url"])
            ataque_esp = next(
                (
                    entry["name"]
                    for entry in move_info["names"]
                    if entry["language"]["name"] == "es"
                ),
                move["move"]["name"].capitalize(),
            )
            ataques.append(ataque_esp)

        # Obtener las habilidades
        habilidades_comun = []
        habilidades_oculta = []
        for ability in resultado["abilities"]:
            ability_info = await peticion(ability["ability"]["url"])
            habilidad_esp = next(
                (
                    entry["name"]
                    for entry in ability_info["names"]
                    if entry["language"]["name"] == "es"
                ),
                ability["ability"]["name"].capitalize(),
            )
            if ability["is_hidden"]:
                habilidades_oculta.append(habilidad_esp)
            else:
                habilidades_comun.append(habilidad_esp)

        descripcion.value = f"Identificando Pokémon:\n\n{descripcion_esp}"
        nombre_pokemon.value = f"#{numero}  {species_info['names'][6]['name']} "
        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{numero}.png"
        imagen.src = sprite_url

        # Traducción de tipos
        tipos_en_espanol = {
            "normal": "Normal",
            "fire": "Fuego",
            "water": "Agua",
            "electric": "Eléctrico",
            "grass": "Planta",
            "ice": "Hielo",
            "fighting": "Lucha",
            "poison": "Veneno",
            "ground": "Tierra",
            "flying": "Volador",
            "psychic": "Psíquico",
            "bug": "Bicho",
            "rock": "Roca",
            "ghost": "Fantasma",
            "dragon": "Dragón",
            "dark": "Siniestro",
            "steel": "Acero",
            "fairy": "Hada",
        }
        tipos = " - ".join(
            [tipos_en_espanol[t["type"]["name"]] for t in resultado["types"]]
        )
        tipo_pokemon_text.value = f"Tipo: {tipos}"

        # Mostrar los ataques
        ataques_texto = "\n".join(ataques)
        ataques_container.content = ft.Column(
            [
                ft.Text(
                    value="Ataques:", color=ft.colors.BLACK, size=10, font_family="zpix"
                ),
                ft.Text(
                    value=ataques_texto,
                    color=ft.colors.BLACK,
                    size=9,
                    font_family="zpix",
                ),
            ]
        )

        # Mostrar las habilidades
        habilidades_texto_comun = "\n".join(habilidades_comun)
        habilidades_texto_oculta = "\n".join(habilidades_oculta)
        habilidades_container.content = ft.Column(
            [
                ft.Text(
                    value=f"Habilidad común:\n{habilidades_texto_comun}",
                    color=ft.colors.BLACK,
                    size=11,
                    font_family="zpix",
                ),
                ft.Text(
                    value=f"Habilidad oculta:\n{habilidades_texto_oculta}",
                    color=ft.colors.BLACK,
                    size=11,
                    font_family="zpix",
                ),
            ]
        )

        await page.update_async()

    async def buscar_pokemon(e):
        query = buscador.value.strip().lower()
        if query.isnumeric():
            numero = int(query)
        else:
            resultado = await peticion(f"https://pokeapi.co/api/v2/pokemon/{query}")
            numero = resultado["id"]
        await actualizar_pokemon(numero)

    async def blink():
        while True:
            await asyncio.sleep(1)
            luz_azul.bgcolor = ft.colors.BLUE_100
            await page.update_async()
            await asyncio.sleep(0.1)
            luz_azul.bgcolor = ft.colors.BLUE
            await page.update_async()

    ## Interfaz del programa
    luz_azul = ft.Container(
        width=35, height=35, left=2.5, top=2.5, bgcolor=ft.colors.BLUE, border_radius=25
    )
    boton_azul = ft.Stack(
        [
            ft.Container(
                width=40, height=40, bgcolor=ft.colors.WHITE, border_radius=25
            ),
            luz_azul,
        ]
    )

    buscador = ft.TextField(
        hint_text="Buscar",
        bgcolor=ft.colors.LIGHT_BLUE_100,
        width=150,
        on_submit=buscar_pokemon,
    )

    items_superior = [
        ft.Container(boton_azul, width=40, height=40),
        ft.Container(width=30, height=20, bgcolor=ft.colors.RED_200, border_radius=25),
        ft.Container(width=30, height=20, bgcolor=ft.colors.YELLOW, border_radius=25),
        ft.Container(width=30, height=20, bgcolor=ft.colors.GREEN, border_radius=25),
        ft.Container(buscador, width=150, margin=ft.margin.only(left=20)),
    ]

    imagen = ft.Image(
        src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
        scale=10,  # Redimensionamos a tamaño muy grande
        width=15,  # Con esto se reescalará a un tamaño inferior automáticamente
        height=15,
        top=275 / 2,
        right=375 / 2,
    )

    nombre_pokemon = ft.Text(value=" #1  Bulbasaur ", color=ft.colors.BLACK, size=14)

    tipo_pokemon_text = ft.Text(
        value=" Planta - Veneno", color=ft.colors.BLACK, size=14
    )

    stack_central = ft.Stack(
        [
            ft.Container(
                width=350,
                height=250,
                bgcolor=ft.colors.WHITE,
                border_radius=10,
            ),
            ft.Container(
                width=300, height=200, bgcolor=ft.colors.BLACK, top=22.5, left=22.5
            ),
            imagen,
        ]
    )

    triangulo = ft.canvas.Canvas(
        [
            ft.canvas.Path(
                [
                    ft.canvas.Path.MoveTo(20, 0),
                    ft.canvas.Path.LineTo(0, 25),
                    ft.canvas.Path.LineTo(40, 25),
                ],
                paint=ft.Paint(
                    style=ft.PaintingStyle.FILL,
                ),
            ),
        ],
        width=40,
        height=25,
    )

    flecha_superior = ft.Container(
        triangulo, width=40, height=25, on_click=evento_get_pokemon
    )

    flechas = ft.Column(
        [
            flecha_superior,
            # radianes 180 grados = 3.14159
            ft.Container(
                triangulo,
                width=40,
                height=25,
                rotate=ft.Rotate(angle=3.14159),
                on_click=evento_get_pokemon,
            ),
        ]
    )

    descripcion = ft.Text(
        value="Identificando Pokémon:\n...", color=ft.colors.BLACK, size=11
    )

    items_inferior = [
        ft.Container(width=25),
        ft.Container(
            descripcion,
            padding=5,
            width=200,
            height=110,
            bgcolor=ft.colors.GREEN,
            border_radius=10,
        ),
        ft.Container(width=15),
        ft.Container(flechas, width=40, height=60),
    ]

    ataques_container = ft.Container(
        padding=20,
        width=135,
        height=100,
        bgcolor=ft.colors.BLUE_100,
        border_radius=10,
        margin=ft.margin.only(left=20, right=10, top=20),
    )

    habilidades_container = ft.Container(
        padding=20,
        width=135,
        height=100,
        bgcolor=ft.colors.BLUE_100,
        border_radius=10,
        margin=ft.margin.only(left=10, right=20, top=20),
    )

    superior = ft.Container(
        content=ft.Row(items_superior),
        width=350,
        height=40,
        margin=ft.margin.only(top=0),
    )
    centro = ft.Container(
        stack_central,
        width=350,
        height=250,
        margin=ft.margin.only(top=20),
        alignment=ft.alignment.center,
    )
    nombre_numero_container = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    nombre_pokemon,
                    bgcolor=ft.colors.BLUE_100,
                    padding=ft.padding.all(10),
                    border_radius=5,
                ),
                ft.Container(
                    tipo_pokemon_text,
                    bgcolor=ft.colors.BLUE_100,
                    padding=ft.padding.all(10),
                    border_radius=5,
                    margin=ft.margin.only(left=10),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # Centramos los contenedores de nombre y tipo
        ),
        alignment=ft.alignment.center,  # Centramos el contenedor
        margin=ft.margin.only(top=20),
    )
    inferior = ft.Container(
        content=ft.Column(
            [ft.Row(items_inferior), ft.Row([ataques_container, habilidades_container])]
        ),
        width=350,
        height=200,
        margin=ft.margin.only(top=20),
    )

    col = ft.Column(
        spacing=0,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            superior,
            centro,
            nombre_numero_container,
            inferior,
        ],
    )

    contenedor = ft.Container(
        col,
        width=390,
        height=800,
        bgcolor=ft.colors.RED,
        alignment=ft.alignment.center,
    )

    await page.add_async(contenedor)
    await blink()


ft.app(target=main)
