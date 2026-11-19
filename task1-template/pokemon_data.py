"""Pokémon data shared by the Play and Stats pages."""
import difflib

import requests
import streamlit as st

# ── Data ──────────────────────────────────────────────────────────────────────────────────
# The 151 first-generation Pokémon (names and order follow https://pokeapi.co/api/v2/pokemon?limit=151).
# A Pokémon's position in this list + 1 is its Pokédex number, which we also need for the image URL.
POKEMON = """
bulbasaur ivysaur venusaur charmander charmeleon charizard squirtle wartortle blastoise
caterpie metapod butterfree weedle kakuna beedrill pidgey pidgeotto pidgeot rattata raticate
spearow fearow ekans arbok pikachu raichu sandshrew sandslash nidoran-f nidorina nidoqueen
nidoran-m nidorino nidoking clefairy clefable vulpix ninetales jigglypuff wigglytuff zubat golbat
oddish gloom vileplume paras parasect venonat venomoth diglett dugtrio meowth persian psyduck
golduck mankey primeape growlithe arcanine poliwag poliwhirl poliwrath abra kadabra alakazam
machop machoke machamp bellsprout weepinbell victreebel tentacool tentacruel geodude graveler
golem ponyta rapidash slowpoke slowbro magnemite magneton farfetchd doduo dodrio seel dewgong
grimer muk shellder cloyster gastly haunter gengar onix drowzee hypno krabby kingler voltorb
electrode exeggcute exeggutor cubone marowak hitmonlee hitmonchan lickitung koffing weezing
rhyhorn rhydon chansey tangela kangaskhan horsea seadra goldeen seaking staryu starmie mr-mime
scyther jynx electabuzz magmar pinsir tauros magikarp gyarados lapras ditto eevee vaporeon
jolteon flareon porygon omanyte omastar kabuto kabutops aerodactyl snorlax articuno zapdos
moltres dratini dragonair dragonite mewtwo mew
""".split()
# Official artwork from the PokeAPI sprites repository (https://github.com/PokeAPI/sprites); {} = Pokédex number
IMAGE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{}.png"
# German names, same order as POKEMON (source: https://www.pokewiki.de/Pokémon-Liste)
NAMES_DE = """
Bisasam Bisaknosp Bisaflor Glumanda Glutexo Glurak Schiggy Schillok Turtok Raupy Safcon Smettbo
Hornliu Kokuna Bibor Taubsi Tauboga Tauboss Rattfratz Rattikarl Habitak Ibitak Rettan Arbok
Pikachu Raichu Sandan Sandamer Nidoran♀ Nidorina Nidoqueen Nidoran♂ Nidorino Nidoking Piepi
Pixi Vulpix Vulnona Pummeluff Knuddeluff Zubat Golbat Myrapla Duflor Giflor Paras Parasek
Bluzuk Omot Digda Digdri Mauzi Snobilikat Enton Entoron Menki Rasaff Fukano Arkani Quapsel
Quaputzi Quappo Abra Kadabra Simsala Machollo Maschock Machomei Knofensa Ultrigaria Sarzenia
Tentacha Tentoxa Kleinstein Georok Geowaz Ponita Gallopa Flegmon Lahmus Magnetilo Magneton
Porenta Dodu Dodri Jurob Jugong Sleima Sleimok Muschas Austos Nebulak Alpollo Gengar Onix
Traumato Hypno Krabby Kingler Voltobal Lektrobal Owei Kokowei Tragosso Knogga Kicklee Nockchan
Schlurp Smogon Smogmog Rihorn Rizeros Chaneira Tangela Kangama Seeper Seemon Goldini Golking
Sterndu Starmie Pantimos Sichlor Rossana Elektek Magmar Pinsir Tauros Karpador Garados Lapras
Ditto Evoli Aquana Blitza Flamara Porygon Amonitas Amoroso Kabuto Kabutops Aerodactyl Relaxo
Arktos Zapdos Lavados Dratini Dragonir Dragoran Mewtu Mew
""".split()
# German names of the Pokémon types (PokeAPI delivers them in English)
TYPE_DE = {
    "normal": "Normal", "fire": "Feuer", "water": "Wasser", "electric": "Elektro",
    "grass": "Pflanze", "ice": "Eis", "fighting": "Kampf", "poison": "Gift",
    "ground": "Boden", "flying": "Flug", "psychic": "Psycho", "bug": "Käfer",
    "rock": "Gestein", "ghost": "Geist", "dragon": "Drache", "dark": "Unlicht",
    "steel": "Stahl", "fairy": "Fee",
}
# small front sprite, used as chat avatar
SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"


def display_name(pokemon):
    """'charizard' -> 'Glurak' (German name)"""
    return NAMES_DE[POKEMON.index(pokemon)]


def suggest(text, limit=5):
    """German names that start with, contain or look like the typed text (typos allowed)."""
    text = text.strip().lower()
    lower = [name.lower() for name in NAMES_DE]
    starts = [n for n in lower if n.startswith(text)]
    contains = [n for n in lower if text in n]
    close = difflib.get_close_matches(text, lower, n=limit, cutoff=0.6)
    best = list(dict.fromkeys(starts + contains + close))[:limit]  # no duplicates, best first
    return [NAMES_DE[lower.index(n)] for n in best]


@st.cache_data  # one request per Pokémon is enough, later calls come from the cache
def get_types(number):
    """Look up the type(s) of a Pokémon by Pokédex number, e.g. ['Feuer', 'Flug']."""
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{number}", timeout=5)
    response.raise_for_status()  # a failed request raises an error, which is not cached
    return [TYPE_DE.get(t["type"]["name"], t["type"]["name"].title())
            for t in response.json()["types"]]


@st.cache_data
def get_facts(number):
    """Facts about a Pokémon from PokeAPI as plain text; they go into the LLM prompt, so the
    LLM does not have to guess. The Pokémon's own name is hidden as '[SECRET]'."""
    api = "https://pokeapi.co/api/v2/"
    pokemon = requests.get(f"{api}pokemon/{number}", timeout=5)
    species = requests.get(f"{api}pokemon-species/{number}", timeout=5)
    pokemon.raise_for_status()
    species.raise_for_status()
    pokemon, species = pokemon.json(), species.json()
    chain = requests.get(species["evolution_chain"]["url"], timeout=5)
    chain.raise_for_status()

    def label(slug):  # evolution names -> German if possible, the Pokémon itself stays hidden
        if slug == POKEMON[number - 1]:
            return "[SECRET]"
        return display_name(slug) if slug in POKEMON else slug.title()

    def family(node):  # walks through the evolution tree and collects all names
        names = [label(node["species"]["name"])]
        for evolution in node["evolves_to"]:
            names += family(evolution)
        return names

    parent = species["evolves_from_species"]
    habitat = species["habitat"]
    return "\n".join([
        "- Types: " + ", ".join(get_types(number)),
        f"- Height: {pokemon['height'] / 10} m, weight: {pokemon['weight'] / 10} kg",
        "- Color: " + species["color"]["name"],
        "- Habitat: " + (habitat["name"] if habitat else "unknown"),
        "- Legendary or mythical: " + ("yes" if species["is_legendary"] or species["is_mythical"] else "no"),
        "- Evolves from: " + (label(parent["name"]) if parent else "nothing (it is a basic form)"),
        "- Evolution family: " + ", ".join(family(chain.json()["chain"])),
    ])
