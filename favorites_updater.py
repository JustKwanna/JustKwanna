from python_graphql_client import GraphqlClient
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://graphql.anilist.co")


TOKEN = os.environ.get("eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjEzNmNhYmFmZDIzMWU2YzgxYmJjOGJhNDI3NTQzNGMyMGJiNDVlOGUyZTA5NTgyZTc1NzU5Yjc0ZTU1MmYxMGUyZTFmYjdjODIxOWJkMzAwIn0.eyJhdWQiOiI0MDM1IiwianRpIjoiMTM2Y2FiYWZkMjMxZTZjODFiYmM4YmE0Mjc1NDM0YzIwYmI0NWU4ZTJlMDk1ODJlNzU3NTliNzRlNTUyZjEwZTJlMWZiN2M4MjE5YmQzMDAiLCJpYXQiOjE1OTkyOTczNTIsIm5iZiI6MTU5OTI5NzM1MiwiZXhwIjoxNjMwODMzMzUyLCJzdWIiOiI2NzkwMTgiLCJzY29wZXMiOltdfQ.iwTfX3XsltffAhCPaCMyUX9t2Uqt-27HCAAZ3RjLndUUGFq340f2QuCXl8lvI1vrWwz43YnIbMmVK6f5rhalGesL8-PAC-TIsAMqb96_yiKSmj3ro7URbjraDC2ZeheuSJ-W_l_785MSIlOY_87eK_t4aDNoNIixdxOi0qPJWClEofx7DnWXYd1E_FP4SuotGKluEV-KZ7TTZThEo3cTa3inQMyFRUNyRS7bbG6YIEZRk4r33tqrSxKG7kfNU7IJxOl0LZOpLviUr5HZV1T9YK9ubmO_lu1TmVIoR57krJQevmgBYET61HtEjzgtRDCx4_EecM60s2d9Ws5X6gf3cUw3QSFo0nVYII5Kjp9FOLSVmvdjBIQBbjAaiZyfP7Ky_amJJN3ftvvpBO-i6qRm3meW6TfIU_6pWK5tlh7LbjbGIoiCdLDfcnLW9o4rr00efV1Qu8z7ggLH-gSXd_Lu49bSLFuX8Nw9B-nRwK0I36ks_4SoyYpe_2vM68mAXvewX6kevInMhlYeUy4rlWftBP__ucOcZxsUeE-poR4WZ90Qq5bCsIZQPWon19C5i3-S8F8VnrOwpoR9yrzcjTfuF2yM6nwQN0aNTl8-SiENkvKUewuo0CPI7AlrxHmgl-6NxnWwnnm7Z-DMdL8R_2QyGLv1vS2Posl_wHA1MHuF0A0", "")


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
