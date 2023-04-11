"""
Script to rewrite redirects

redirects for gh-pages to readthedocs
"""

from pathlib import Path

redirect_tpl = """\
<html>
<head>
  <link rel="canonical" href="{url}" />
  <script type="text/javascript">
  // preserve url params
  u = new URL(document.location.href);
  u.host = "{host}";
  u.host = "nbgitpuller.readthedocs.io";
  // replace '/nbgitpuller/' prefix with '/en/latest'
  path_list = u.pathname.split("/");
  path_list.splice(1, 1, "en", "latest");
  u.pathname = path_list.join("/");
  if ({add_html} && u.pathname.slice(-5) !== ".html") {{
    // preserve gh-pages auto-add .html
    // e.g. https://hub.jupyter.org/nbgitpuller/link
    u.pathname += ".html";
  }}
  window.location = u.toString();
  </script>
</head>
<body>
This page has moved to <a href="{url}">{url}</a>.
</body>
</html>
"""

root_dir = Path(__file__).parent.resolve()

host = "nbgitpuller.readthedocs.io"
base_url = f"https://{host}/en/latest/"


def rewrite_page(path):
    sub_path = str(path.relative_to(root_dir))
    url = base_url + sub_path
    print(path, url)
    new_html = redirect_tpl.format(
        host=host, url=url, add_html=str(path.name != "index.html").lower()
    )
    with path.open("w") as f:
        f.write(new_html)


def main():
    for path in root_dir.glob("**/*.html"):
        rewrite_page(path)


if __name__ == "__main__":
    main()
