#!/usr/bin/env python3
"""
Comprehensive Genre Mapping (2000-2025)
Includes 300+ artists across all eras
"""

# Start with existing mapping
from multi_genre_analyzer import MULTI_GENRE_MAPPING

# Massive expansion for 2000-2015 era
COMPREHENSIVE_GENRE_MAPPING = {
    **MULTI_GENRE_MAPPING,  # Keep existing mappings

    # === POP (2000s-2010s) ===
    "Kelly Clarkson": "Pop",
    "Maroon 5": "Pop",
    "P!nk": "Pop",
    "Bruno Mars": "Pop",
    "Justin Timberlake": "Pop/R&B",
    "Britney Spears": "Pop",
    "Adele": "Pop",
    "Ke$ha": "Pop",
    "Ed Sheeran": "Pop",
    "One Direction": "Pop",
    "Ellie Goulding": "Pop",
    "Justin Bieber": "Pop",
    "Demi Lovato": "Pop",
    "Meghan Trainor": "Pop",
    "Lorde": "Pop",
    "Gwen Stefani": "Pop",
    "Sara Bareilles": "Pop",
    "Madonna": "Pop",
    "Jessica Simpson": "Pop",
    "Christina Aguilera": "Pop",
    "Sia": "Pop",
    "LMFAO": "Pop/Dance",
    "Flo Rida": "Pop/Hip-Hop",
    "Jason Derulo": "Pop/R&B",
    "Pitbull": "Pop/Latin/Hip-Hop",
    "Avicii": "Pop/EDM",
    "Sam Smith": "Pop/R&B",
    "Fergie": "Pop/Hip-Hop",
    "Nelly Furtado": "Pop",
    "Natasha Bedingfield": "Pop",
    "Jordin Sparks": "Pop/R&B",
    "Leona Lewis": "Pop/R&B",
    "The Pussycat Dolls": "Pop",
    "Jennifer Lopez": "Pop/Latin",
    "Katy Perry": "Pop",  # Update if not already there

    # === R&B (2000s-2010s) ===
    "Alicia Keys": "R&B",
    "Ne-Yo": "R&B",
    "Mariah Carey": "R&B/Pop",
    "Ashanti": "R&B",
    "Mary J. Blige": "R&B",
    "Aaliyah": "R&B",
    "R. Kelly": "R&B",
    "Akon": "R&B/Hip-Hop",
    "Sean Kingston": "R&B/Pop",
    "Trey Songz": "R&B",
    "John Legend": "R&B",
    "Mario": "R&B",
    "Jordin Sparks": "R&B/Pop",
    "Destiny's Child": "R&B/Pop",

    # === HIP-HOP/RAP (2000s-2010s) ===
    "Eminem": "Hip-Hop",
    "Kanye West": "Hip-Hop",
    "Ye": "Hip-Hop",
    "50 Cent": "Hip-Hop",
    "T.I.": "Hip-Hop",
    "JAY-Z": "Hip-Hop",
    "Sean Paul": "Hip-Hop/Reggae",
    "Ludacris": "Hip-Hop",
    "Nelly": "Hip-Hop",
    "Lil Wayne": "Hip-Hop",
    "OutKast": "Hip-Hop",
    "Missy Elliott": "Hip-Hop",
    "Missy \"Misdemeanor\" Elliott": "Hip-Hop",

    # Collaborations
    "The Black Eyed Peas": "Hip-Hop/Pop",
    "Eminem Featuring Rihanna": "Hip-Hop",
    "Lil Wayne Featuring Drake": "Hip-Hop",
    "Beyonce Featuring Jay Z": "R&B/Hip-Hop",
    "Mark Ronson Featuring Bruno Mars": "Pop/Funk",
    "LMFAO Featuring Lauren Bennett & GoonRock": "Pop/Dance",
    "Jennifer Lopez Featuring Ja Rule": "Pop/Hip-Hop",

    # === COUNTRY (2000s-2010s) ===
    "Carrie Underwood": "Country",
    "Kenny Chesney": "Country",
    "Luke Bryan": "Country",
    "Lady Antebellum": "Country",
    "Tim McGraw": "Country",
    "Toby Keith": "Country",
    "Rascal Flatts": "Country",
    "Jason Aldean": "Country",
    "Blake Shelton": "Country",
    "Keith Urban": "Country",
    "Zac Brown Band": "Country",
    "Brad Paisley": "Country",
    "The Band Perry": "Country",
    "Florida Georgia Line": "Country",
    "Dierks Bentley": "Country",

    # === ROCK/ALTERNATIVE (2000s-2010s) ===
    "Nickelback": "Rock",
    "Fall Out Boy": "Rock",
    "Linkin Park": "Rock",
    "3 Doors Down": "Rock",
    "Train": "Rock/Pop",
    "Coldplay": "Alternative/Rock",
    "matchbox twenty": "Rock",
    "The Fray": "Alternative/Rock",
    "Lifehouse": "Rock",
    "Daughtry": "Rock",
    "The All-American Rejects": "Rock",
    "Green Day": "Rock",
    "Creed": "Rock",
    "Paramore": "Rock",
    "Finger Eleven": "Rock",
    "Staind": "Rock",
    "Avril Lavigne": "Pop/Rock",
    "John Mayer": "Pop/Rock",
    "Jason Mraz": "Pop/Rock",
    "Colbie Caillat": "Pop/Rock",
    "Gavin DeGraw": "Pop/Rock",
    "Dido": "Alternative/Pop",
    "Michelle Branch": "Pop/Rock",

    # === ADDITIONAL MAJOR ARTISTS ===
    "Rihanna": "Pop/R&B",
    "Lady Gaga": "Pop",
    "Katy Perry": "Pop",
    "Shakira": "Pop/Latin",
    "Enrique Iglesias": "Pop/Latin",
    "Pitbull": "Hip-Hop/Latin",
    "Taio Cruz": "Pop/R&B",
    "David Guetta": "Pop/EDM",
    "Calvin Harris": "Pop/EDM",
    "OneRepublic": "Pop/Rock",
    "The Script": "Pop/Rock",
    "Fun.": "Alternative/Pop",
    "Gotye": "Alternative/Pop",
    "Macklemore & Ryan Lewis": "Hip-Hop",
    "Iggy Azalea": "Hip-Hop",
    "Nicki Minaj": "Hip-Hop",
    "Wiz Khalifa": "Hip-Hop",
    "Rick Ross": "Hip-Hop",
    "Kendrick Lamar": "Hip-Hop",
    "J. Cole": "Hip-Hop",
    "Big Sean": "Hip-Hop",
}

# Add more comprehensive mappings for features/collaborations
COLLABORATION_MAPPINGS = {
    # Common featuring patterns - use primary artist's genre
    "Featuring": "primary_artist",  # Logic: classify by first artist
}

def get_genre(artist_name):
    """
    Get genre for an artist, handling collaborations
    """
    if artist_name in COMPREHENSIVE_GENRE_MAPPING:
        return COMPREHENSIVE_GENRE_MAPPING[artist_name]

    # Handle "Featuring" collaborations - use primary artist
    if " Featuring " in artist_name or " Feat. " in artist_name:
        primary = artist_name.split(" Featuring ")[0].split(" Feat. ")[0]
        if primary in COMPREHENSIVE_GENRE_MAPPING:
            return COMPREHENSIVE_GENRE_MAPPING[primary]

    # Handle "&" collaborations - use first artist
    if " & " in artist_name:
        primary = artist_name.split(" & ")[0]
        if primary in COMPREHENSIVE_GENRE_MAPPING:
            return COMPREHENSIVE_GENRE_MAPPING[primary]

    return None

# Export count
print(f"Comprehensive Genre Mapping: {len(COMPREHENSIVE_GENRE_MAPPING)} artists")

if __name__ == "__main__":
    # Show genre breakdown
    from collections import Counter

    genres = Counter()
    for artist, genre in COMPREHENSIVE_GENRE_MAPPING.items():
        # Split multi-genre classifications
        if "/" in genre:
            primary_genre = genre.split("/")[0]
        else:
            primary_genre = genre

        genres[primary_genre] += 1

    print("\nGenre Distribution:")
    print("="*50)
    for genre, count in genres.most_common():
        print(f"{genre:<20} {count:>5} artists")

    print(f"\nTotal: {len(COMPREHENSIVE_GENRE_MAPPING)} artists mapped")
