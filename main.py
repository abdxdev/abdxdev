import datetime
from urllib.parse import quote

import requests


PORTFOLIO_API = "https://abd-dev.studio/api/portfolio?fetch=true"


class Helper:
    @staticmethod
    def list_dict_to_list_list(data):
        """
        Converts a list of dictionaries into a list of lists where the first list contains the keys,
        and subsequent lists contain the corresponding values.
        If a value is a list, it joins the elements with a space.
        For example:
        [{"a": 1, "b": 2}, {"a": 3, "b": 4}] becomes [["a", "b"], [1, 2], [3, 4]].
        """
        if not data:
            return []

        headers = list(data[0].keys())

        def format_value(value):
            if isinstance(value, list):
                return " ".join(map(str, value))
            return str(value)

        values = [[format_value(value) for value in item.values()] for item in data]
        return [headers] + values

    @staticmethod
    def list_dict_to_transformed_list(data):
        """
        Transforms a list of dictionaries into a list of lists where each inner list
        contains the values corresponding to the same key across all dictionaries.
        For example:
        [{"a": 1, "b": 2}, {"a": 3, "b": 4}] becomes [[1, 3], [2, 4]].
        """
        if not data:
            return []
        grouped_dict = {key: [] for key in data[0]}
        for item in data:
            for key, value in item.items():
                grouped_dict[key].append(str(value))
        return [grouped_dict[key] for key in grouped_dict]

    @staticmethod
    def short_string(text, max=20):
        if len(text) > max:
            return text[: max - 5] + "..." + text[-5:]
        return text


class GHMarkdown:
    def __init__(self):
        self.md = ""

    def write(self, text, centered=True, summary="", sep="\n\n"):
        if centered:
            self.md += '<div align="center">\n\n'
        if summary:
            self.md += f"<details><summary>{summary}</summary>\n\n"
        self.md += text.strip() + sep
        if summary:
            self.md += "</details>\n\n"
        if centered:
            self.md += "</div>\n\n"

    @staticmethod
    def heading(text):
        return open("assets/md/heading_template.md").read().strip().replace(r"{heading}", text)

    @staticmethod
    def table(data, centered=False, header=True):
        """
        Creates a Markdown table from a list of lists.
        The first inner list is treated as the header.
        For example:
        [["Header1", "Header2"], ["Row1Col1", "Row1Col2"], ["Row2Col1", "Row2Col2"]]
        becomes:
        | Header1 | Header2 |
        | --- | --- |
        | Row1Col1 | Row1Col2 |
        | Row2Col1 | Row2Col2 |
        """
        if not data:
            return ""
        head = f"| {' | '.join(data[0])} |\n"
        separator = "| " + " | ".join([":---:" if centered else "---" for _ in data[0]]) + " |\n"
        rows = "".join([f"| {' | '.join(row)} |\n" for row in data[1:]])
        if header:
            return head + separator + rows
        return head + rows

    @staticmethod
    def get_gallery_view(dict_item: list[dict[str, str]], columns: int):
        """
        Generates a Markdown gallery view from a list of dictionaries.
        For example, each dictionary could represent an item with its title and poster.
        """
        chunks = []
        for i in range(0, len(dict_item), columns):
            sl = slice(i, i + columns)
            for key in dict_item[i].keys():
                chunks.append([item[key] for item in dict_item[sl]])
        return GHMarkdown.table(chunks, centered=True)

    @staticmethod
    def image(alt, src):
        return f"![{alt}](<{src}>)"

    @staticmethod
    def html_image(alt, src, width=20):
        return f'<img src="{src}" alt="{alt}" width="{width}">'

    @staticmethod
    def link(text, url):
        return f"[{text}]({url})"

    @staticmethod
    def html_link(text, url):
        return f'<a href="{url}" target="_blank">{text}</a>'

    def __str__(self):
        return self.md.strip()

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.md.strip())


def get_anime(animelist):
    formatted_animes = {}

    for anime in animelist:
        status = anime["status"]
        if status not in formatted_animes:
            formatted_animes[status] = []

        formatted_anime = {
            "Title": Helper.short_string(anime["title"], max=20),
            "Poster": f"[![{anime['title']}]({anime['cover_image']})]({anime['site_url']})",
        }
        formatted_animes[status].append(formatted_anime)

    md = GHMarkdown()

    for category, dict_item in formatted_animes.items():
        table = GHMarkdown.get_gallery_view(dict_item, 4)
        md.write(table, centered=False, summary=category.replace("_", " ").title())

    return str(md)


def get_games(games):
    formatted_games = {}

    for game in games:
        status = game["status"]
        if status not in formatted_games:
            formatted_games[status] = []

        formatted_game = {
            "Title": Helper.short_string(game["name"], max=20),
            "Poster": f"[![{game['name']}]({game['background_image_cropped']})]({game['rawg_link']})",
        }
        formatted_games[status].append(formatted_game)

    md = GHMarkdown()

    for category, dict_item in formatted_games.items():
        table = GHMarkdown.get_gallery_view(dict_item, 3)
        md.write(table, centered=False, summary=category.replace("_", " ").title())

    return str(md)


def get_friends(friends):
    formatted_friends = []
    for friend in friends:
        formatted_friend = {
            "Name": friend["github_name"],
            "Avatar": GHMarkdown.link(GHMarkdown.image(friend["github_name"], friend["github_avatar"]), friend["github_url"]),
            "Link": GHMarkdown.link("@" + friend["github_username"], friend["github_url"]),
        }
        formatted_friends.append(formatted_friend)

    return GHMarkdown.get_gallery_view(formatted_friends, 3)


# def get_all_projects(projects):
#     md = GHMarkdown()
#     for project in projects:
#         if project["Project"] == "":
#             continue
#         md.write(f"- {project['Project']}: {project['Description']} \\| `{project['Created']}`", centered=False)
#         # md.write(f"- {project['Project']}: {project['Description']} \\| ![{project['Created']}](https://img.shields.io/badge/{project['Created']}-ffffff?style=for-the-badge&color=080808)\n", centered=False)
#     return str(md)


def get_projects_list(projects, choosing_condition_func):
    formatted_projects = []

    for project in projects:
        priority = project["priority"]
        if priority is None:
            priority = float("inf")

        prefix = []
        if priority == 0:
            prefix.append("⭐")
        if project["is_university_project"]:
            prefix.append("`UNI`")
        if project["working_on"]:
            prefix.append("`WIP`")
            priority = 1

        if choosing_condition_func(project) if choosing_condition_func else True:
            formatted_projects.append(
                {
                    "Name": (f'{" ".join(prefix)} ' if prefix else "") + f'**{GHMarkdown.link(project["title"], project["html_url"])}**',
                    "Description": project["description"].strip() + (rf" \| {GHMarkdown.link('🌐', project['homepage'])} " if project["homepage"] else ""),
                    "Created": project["created_at"].split("T")[0][:4],
                },
            )

    return GHMarkdown.table(Helper.list_dict_to_list_list(formatted_projects))


def get_projects_gallery(projects, choosing_condition_func):
    formatted_projects = []

    for project in projects:
        priority = project["priority"]
        if priority is None:
            priority = float("inf")

        prefix = []
        if priority == 0:
            prefix.append("⭐")
        if project["is_university_project"]:
            prefix.append("`UNI`")
        if project["working_on"]:
            prefix.append("`WIP`")
            priority = 1

        if choosing_condition_func(project) if choosing_condition_func else True:
            image = project["thumbnails"][0] if len(project["thumbnails"]) > 0 else project["default_image_url"]
            formatted_project = {
                "Thumbnail": GHMarkdown.html_link(GHMarkdown.html_image(project["title"], image, 300), project["html_url"]),
                "Name": (f'{" ".join(prefix)} ' if prefix else "") + f'**{GHMarkdown.link(project["title"], project["html_url"])}**' + (rf' {GHMarkdown.link("🌐", project["homepage"])} ' if project["homepage"] else ""),
                "Description": project["description"].strip(),
            }
            formatted_projects.append(formatted_project)

    return GHMarkdown.get_gallery_view(formatted_projects, 3)


def get_all_skills(skills_sets):
    filtered_skills = []

    for category_data in skills_sets:
        filtered_skills.append(
            {
                "Category": category_data["category"],
                "Tools": [
                    GHMarkdown.image(
                        skill["name"],
                        f"https://img.shields.io/badge/{quote(skill['name'])}-{skill['hex'] or '000000'}?logo={skill['slug']}&style=for-the-badge&labelColor=000000&logoColor={'ffffff' if skill['hex'] == '000000' else (skill['hex'] or 'ffffff')}",
                        # f"https://img.shields.io/badge/{quote(skill['name'])}-ffffff?logo={skill['slug']}&style=for-the-badge&color=000000&logoColor={'ffffff' if skill['hex'] == '000000' else (skill['hex'] or 'ffffff')}",
                    )
                    for skill in category_data["skills"]
                ],
            }
        )

    return GHMarkdown.table(Helper.list_dict_to_list_list(filtered_skills))


def get_featured_skills(skills_sets):
    formatted_skills = []

    for category_data in skills_sets:
        for skill in category_data["skills"]:
            if skill["portfolio"]:
                badge = f"https://img.shields.io/badge/{quote(skill['name'])}-{skill['hex'] or '000000'}?logo={skill['slug']}&style=for-the-badge&logoColor=ffffff"
                formatted_skills.append(GHMarkdown.image(skill["name"], badge))

    return " ".join(formatted_skills)


def make_markdown():
    md = GHMarkdown()
    portfolio = requests.get(PORTFOLIO_API).json()

    md.write(open("assets/md/header.md", encoding="utf-8").read())
    md.write(open("assets/md/description.md", encoding="utf-8").read())

    md.write(GHMarkdown.heading("Languages & Tools"))
    md.write(get_featured_skills(portfolio["skills"]))
    md.write(open("assets/md/github_stats.md", encoding="utf-8").read())
    md.write(get_all_skills(portfolio["skills"]), centered=False, summary="See more skills")

    md.write(GHMarkdown.heading("Featured Projects"))
    md.write(get_projects_gallery(portfolio["projects"], lambda x: x["priority"] == 0))
    md.write(get_projects_list(portfolio["projects"], lambda x: x["priority"] != 0), centered=False, summary="See more projects")

    md.write(GHMarkdown.heading("Anime List"))
    md.write('*"Planning to watch" list == "Issues" tab*')
    md.write(open("assets/md/anilist.md", encoding="utf-8").read())
    md.write("<img align='right' src='assets/gif/anime_gif.gif' height='170'>", centered=False)
    md.write(get_anime(portfolio["anime"]), centered=False)

    md.write(GHMarkdown.heading("Game List"))
    md.write("*a professional respawner*")
    # md.write("<img align='right' src='assets/gif/game_gif.gif' height='80'>")
    md.write(get_games(portfolio["games"]), centered=False)

    md.write(GHMarkdown.heading("Hobbies & Interests"))
    md.write(open("assets/md/hobbies.md", encoding="utf-8").read(), centered=False)

    md.write(GHMarkdown.heading("Meet my Code Buddies!"))
    md.write("*From clean code to genius ideas, they're the real MVPs of the dev world. 😎*")
    md.write(get_friends(portfolio["friends"]))

    md.write(GHMarkdown.heading("Support Me"))
    md.write(open("assets/md/supportme.md", encoding="utf-8").read())
    request = requests.Request("GET", "https://abd-utils-server.vercel.app/service/trigger-workflow/", params={"owner": "abdxdev", "repo": "abdxdev", "event": "update-readme", "redirect_uri": "https://github.com/abdxdev"}).prepare().url
    md.write(f"[![Click to Update](https://img.shields.io/badge/Update-Last_Updated:_{str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).replace(' ','_').replace('-', '--')}_UTC-ffffff?style=for-the-badge&color=080808)]({request})")
    md.write("> _This README is auto-generated. If you want to update it, click the button above._")
    md.write(open("assets/md/footer.md", encoding="utf-8").read())

    md.save("README.md")


if __name__ == "__main__":
    make_markdown()
