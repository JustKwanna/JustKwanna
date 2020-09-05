from python_graphql_client import GraphqlClient
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://graphql.anilist.co")


TOKEN = os.environ.get("def50200762352d87198e320bb3cd70d64972bf9d930870d4a763b1419f590aa9d51cb2169a316a0e506a6785a9e608ab32d121f244afa3f21f140b1cd6d88675bbfc307b0d00c90a6cdec55af86eb9d8f382333b96540025352ce9a57c19372918a1e004c239e25fd0befbd11f1079ed9fe535ea5d855723deafc5db829a1d20ef027896598b7003b3fd971ddd7867a45096f519320820101bd12914a37f892572f1e6f77b0ee24ed5d884e8ca2e1bf588323a9b3d259c81f3dd4481fc8624254d7679c7c6e67f083e642a9b95d56f90728f699fd106ba94130072001555a84f747d8177e4c0cfcd31133b2f55609e2df144f2d39d9755e83c4f97e9bded75b80251dd818ab4e4b81161eedeefb5ad5f6b604b8cb09c9edca8c40e5e660e135e4090e3fc4f38a47f95e58054da27b07e141719ae0b2c0c9d52f3a50bb6205037c12096bdcd231ac3fd4a1f65c", "")


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)

def make_query():
    return """
query($favPage: Int) {
  Viewer {
    favourites {
      anime(page: $favPage) {
        nodes {
          title {
            romaji
          }
          siteUrl
        }
        pageInfo {
          total
          currentPage
          lastPage
          perPage
          hasNextPage
        }
      }
      manga(page: $favPage) {
        nodes {
          title {
            romaji
          }
          siteUrl
        }
        pageInfo {
          total
          currentPage
          lastPage
          perPage
          hasNextPage
        }
      }
      characters(page: $favPage) {
        nodes {
          name {
            full
          }
          siteUrl
        }
        pageInfo {
          total
          currentPage
          lastPage
          perPage
          hasNextPage
        }
      }
    }
  }
}
"""

def fetch_favorites(oauth_token, types='anime'):
    results = []
    variables = {"favPage": 1}
    data = client.execute(
        query=make_query(),
        variables=variables,
        headers={"Authorization": "Bearer {}".format(oauth_token)},
    )
    for x in data['data']['Viewer']['favourites'][types]['nodes']:
        results.append(
            {
                'title': x['title']['romaji'] if types != 'characters' else x['name']['full'],
                'url': x['siteUrl']
            }
        )
    return results   

if __name__ == "__main__":
    readme = root / "README.md"
    readme_contents = readme.open().read()
    # Favorites Anime
    data = fetch_favorites(TOKEN, types='anime')
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    print (res)
    rewritten = replace_chunk(readme_contents, "favorites_anime", res)
    # Favorites Manga
    data = fetch_favorites(TOKEN, types='manga')
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    print (res)
    rewritten = replace_chunk(readme_contents, "favorites_manga", res)
    # Favorites Characters
    data = fetch_favorites(TOKEN, types='characters')
    res = "\n".join(
        [
            "* [{title}]({url})".format(**x)
            for x in data
        ]
    )
    print (res)
    rewritten = replace_chunk(readme_contents, "favorites_characters", res)
    
    readme.open("w").write(rewritten)
