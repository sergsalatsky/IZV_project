# IZV - Zpracování a vizualizace dat v prostředí Python

## Projekt (část 1): Získání a předzpracování dat
+2 delky vsech datovych sloupcu jsou stejne (az 2 bodu) \
+2 pocet sloupcu je stejny jako pocet hlavicek (az 2 bodu) \
+2 stahlo se 81_501 zaznamu (az 2 bodu) \
+1 uspesne se stahl Plzensky kraj (s chybou) (az 1 bodu) \
+1 podarilo se vytvorit pandas.DataFrame (az 1 bodu) \
+0 rozumne rozlozeni datovych typu (az 1 bodu) \
+0 souradnice jsou spravne jako floaty i s desetinnymi misty (az 1 bodu) \
+0 neni mozne hodnotit cas 2.55 s, jelikoz t1, t4 a t5 neprosly (az 2 bodu) \
+3.00 kvalita kodu downloader.py (az 3 bodu) \
+3.00 kvalita kodu get_stat.py (az 3 bodu) \
+2.00 graf z get_stat.py (az 2 bodu) 

**CELKEM: 16.0 bodu**

## Projekt (část 2): Základní analýza dat
+1.00 pouzite kategoricke typy (>=2) (az 1 bodu) \
+0.00 ostatni typy jsou korektni (ints>30 & floats>=6) (az 1 bodu) \
+1.00 vhodne vyuziti pameti (< 500 MB) (az 1 bodu) \
+1.00 spravne konvertovane datum (rok 2016 - 2020) (az 1 bodu) \
+0.12 funkce get_dataframe ma spravne docstring (PEP257) (az 0.125 bodu) \
+0.12 funkce plot_conseq ma spravne docstring (PEP257) (az 0.125 bodu) \
+0.12 funkce plot_damage ma spravne docstring (PEP257) (az 0.125 bodu) \
+0.12 funkce plot_surface ma spravne docstring (PEP257) (az 0.125 bodu) \
+0.50 funkce plot_conseq trva do 3000 ms (az 0.5 bodu) \
+2.00 kvalita kodu funkce plot_conseq (az 2 bodu) \
+2.00 vizualni dojem z grafu plot_conseq (az 2 bodu) \
+0.50 funkce plot_damage trva do 5000 ms (az 0.5 bodu) \
+2.00 kvalita kodu funkce plot_damage (az 2 bodu) \
+2.00 vizualni dojem z grafu plot_damage (az 2 bodu) \
+0.50 funkce plot_surface trva do 5000 ms (az 0.5 bodu) \
+2.00 kvalita kodu funkce plot_surface (az 2 bodu) \
+2.00 vizualni dojem z grafu plot_surface (az 2 bodu) \
+2.00 kvalita kodu dle PEP8 (0 kritickych, 2 E2.., 0 E7..)) (az 2 bodu)

**CELKEM: 19.0 bodu**

## Projekt: celkové řešení

### Geograficka data
+0.00 spravne CRS (5514, 3857) (az 1 b) \
+0.00 spravne rozsah (viz FAQ) (az 2 b) \
+2.00 pocet radku 485591 > 485e3 (az 2 b) \
+2.00 bez NaN v souradnicich (az 2 b) \
+2.00 plot_geo: prehlednost, vzhled (az 3 b) \
+0.00 plot_geo: zobrazeni ve WebMercator (a ne v S-JTSK) (az 2 b) \
+1.00 plot_cluster: prehlednost, vzhled (az 2 b) \
+3.00 plot_cluster: clustering (az 3 b) \
+1.00 funkce make_geo ma spravne docstring (PEP257) (az 1 b) \
+0.50 funkce plot_geo ma spravne docstring (PEP257) (az 0.5 b) \
+0.50 funkce plot_cluster ma spravne docstring (PEP257) (az 0.5 b) \
+1.00 kvalita kodu dle PEP8 (0 kritickych, 0 E2.., 0 E7..)) (az 1 b)

### Overeni hypotezy
+2.00 filtrace (az 2 b) \
+2.00 kontingencni tabulka (az 2 b) \
+2.00 vypocet chi2 testu (az 2 b) \
+0.00 komentare (az 1 b) \
+3.00 zaver: dochazi k silnemu ovlivneni (az 3 b)

### Vlastni analyza
+5.00 tabulka: prehlednost, vzhled (az 5 b) \
+3.00 graf: popis, vzhled (az 4 b) \
+4.00 graf: vhodna velikost, citelnost (az 4 b) \
+2.00 graf: pouziti vektoroveho formatu (az 2 b) \
+3.00 textovy popis (az 3 b) \
+2.00 statisticka smysluplnost analyzy (az 4 b) \
+1.00 dalsi ciselne hodnoty v textu (az 3 b) \
+0.00 generovani hodnot skriptem bez chyby (az 3 b) \
+2.00 kvalita kodu dle PEP8 (0 kritickych, 4 E2.., 1 E7..)) (az 2 b)

**CELKEM: 44.0 bodu**
