import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from schemas import PasteDetails, UserDetails

# NOTE: Will add specialized exceptions, retry mechanisms, etc

# Possible highlight syntax options from the Pastebin docs.
HIGHLIGHTING_OPTIONS = {
    "4cs", "6502acme", "6502kickass", "6502tasm", "abap", "actionscript",
    "actionscript3", "ada", "aimms", "algol68", "apache", "applescript",
    "apt_sources", "arduino", "arm", "asm", "asp", "asymptote", "autoconf",
    "autohotkey", "autoit", "avisynth", "awk", "bascomavr", "bash",
    "basic4gl", "dos", "bibtex", "b3d", "blitzbasic", "bmx", "bnf", "boo",
    "bf", "c", "csharp", "c_winapi", "cpp", "cpp-winapi", "cpp-qt",
    "c_loadrunner", "caddcl", "cadlisp", "ceylon", "cfdg", "c_mac",
    "chaiscript", "chapel", "cil", "clojure", "klonec", "klonecpp",
    "cmake", "cobol", "coffeescript", "cfm", "css", "cuesheet", "d", "dart",
    "dcl", "dcpu16", "dcs", "delphi", "oxygene", "diff", "div", "dot",
    "e", "ezt", "ecmascript", "eiffel", "email", "epc", "erlang", "euphoria",
    "fsharp", "falcon", "filemaker", "fo", "f1", "fortran", "freebasic",
    "freeswitch", "gambas", "gml", "gdb", "gdscript", "genero", "genie",
    "gettext", "go", "godot-glsl", "groovy", "gwbasic", "haskell", "haxe",
    "hicest", "hq9plus", "html4strict", "html5", "icon", "idl", "ini",
    "inno", "intercal", "io", "ispfpanel", "j", "java", "java5",
    "javascript", "jcl", "jquery", "json", "julia", "kixtart", "kotlin",
    "ksp", "latex", "ldif", "lb", "lsl2", "lisp", "llvm", "locobasic",
    "logtalk", "lolcode", "lotusformulas", "lotusscript", "lscript", "lua",
    "m68k", "magiksf", "make", "mapbasic", "markdown", "matlab", "mercury",
    "metapost", "mirc", "mmix", "mk-61", "modula2", "modula3", "68000devpac",
    "mpasm", "mxml", "mysql", "nagios", "netrexx", "newlisp", "nginx",
    "nim", "nsis", "oberon2", "objeck", "objc", "ocaml", "ocaml-brief",
    "octave", "pf", "glsl", "oorexx", "oobas", "oracle8", "oracle11", "oz",
    "parasail", "parigp", "pascal", "pawn", "pcre", "per", "perl", "perl6",
    "phix", "php", "php-brief", "pic16", "pike", "pixelbender", "pli",
    "plsql", "postgresql", "postscript", "povray", "powerbuilder",
    "powershell", "proftpd", "progress", "prolog", "properties", "providex",
    "puppet", "purebasic", "pycon", "python", "pys60", "q", "qbasic", "qml",
    "rsplus", "racket", "rails", "rbs", "rebol", "reg", "rexx", "robots",
    "roff", "rpmspec", "ruby", "gnuplot", "rust", "sas", "scala", "scheme",
    "scilab", "scl", "sdlbasic", "smalltalk", "smarty", "spark", "sparql",
    "sqf", "sql", "sshconfig", "standardml", "stonescript", "sclang",
    "swift", "systemverilog", "tsql", "tcl", "teraterm", "texgraph",
    "thinbasic", "typescript", "typoscript", "unicon", "uscript", "upc",
    "urbi", "vala", "vbnet", "vbscript", "vedit", "verilog", "vhdl", "vim",
    "vb", "visualfoxpro", "visualprolog", "whitespace", "whois", "winbatch",
    "xbasic", "xml", "xojo", "xorg_conf", "xpp", "yaml", "yara", "z80",
    "zxbasic"
}

# Valid expiration/lifespan values from the Pastebin docs.
LIFESPAN_OPTIONS = {
    "N",    # Never
    "10M",  # 10 Minutes
    "1H",   # 1 Hour
    "1D",   # 1 Day
    "1W",   # 1 Week
    "2W",   # 2 Weeks
    "1M",   # 1 Month
    "6M",   # 6 Months
    "1Y",   # 1 Year
}

# Visibility mappings (Pastebin uses numeric codes internally).
VISIBILITY_MAP_INT_TO_STR = {0: "public", 1: "unlisted", 2: "private"}
VISIBILITY_MAP_STR_TO_INT = {"public": 0, "unlisted": 1, "private": 2}

# Account type mappings (Pastebin uses 0 for normal, 1 for pro).
ACCOUNT_TYPE_MAP_INT_TO_STR = {0: "normal", 1: "pro"}


class PastebinClient:
    """
    A client for interacting with the Pastebin API.

    Provides methods to:
      - Login and retrieve a user session
      - Create a paste
      - Delete a paste
      - Fetch raw paste content
      - List user pastes
      - Get user details
    """

    def __init__(self, dev_key: str):
        """
        :param dev_key: Your Pastebin developer key.
        """
        self.dev_key = dev_key
        self.api_url = "https://pastebin.com/api/"
        self.api_url_raw = "https://pastebin.com/raw/"

        # Defaults set after login:
        self.default_user_key = None
        self.default_highlighting = None
        self.default_expiration = None
        self.default_visibility = None

    def fetch_user_key(self, username: str, password: str) -> str:
        """
        Retrieve a user session key (api_user_key) for the given username/password.

        :param username: The Pastebin account username.
        :param password: The Pastebin account password.
        :return: The user session key as a string.
        :raises Exception: If the request fails or returns a 'Bad API request' error.
        """
        url = self.api_url + "api_login.php"
        data = {
            "api_dev_key": self.dev_key,
            "api_user_name": username,
            "api_user_password": password,
        }
        response = requests.post(url, data=data)

        if response.status_code == 200:
            # Check for known error patterns
            if response.text.startswith("Bad API request"):
                raise Exception(f"Login failure: {response.text.strip()}")
            return response.text.strip()
        else:
            raise Exception(
                f"Failed to fetch user key: {response.status_code} - {response.text}"
            )

    def login(self, username: str, password: str) -> None:
        """
        Login with provided credentials, storing the user session key and user defaults internally.

        :param username: The Pastebin account username.
        :param password: The Pastebin account password.
        """
        self.default_user_key = self.fetch_user_key(username, password)
        user_data = self.user_details(self.default_user_key)
        self.default_highlighting = user_data.default_highlighting
        self.default_expiration = user_data.default_expiration
        self.default_visibility = user_data.default_visibility

    def create_paste(
        self,
        text: str,
        name: str = None,
        highlighting: str = None,
        visibility: str = None,
        lifespan: str = None,
        folder_key: str = None,
        user_key: str = None,
    ) -> "PasteDetails":
        """
        Create a new paste.

        :param text: The text content of the paste (required).
        :param name: An optional title for the paste.
        :param highlighting: e.g. 'python', 'javascript', etc. Must be in HIGHLIGHTING_OPTIONS.
        :param visibility: Must be 'public', 'unlisted', or 'private'.
        :param lifespan: Must be in LIFESPAN_OPTIONS (e.g. '10M', 'N', '1H', etc.).
        :param folder_key: A folder key to place the paste in (requires user key).
        :param user_key: The user key to use for the request (defaults to self.default_user_key).
        :return: A PasteDetails object containing metadata about the newly created paste.
        :raises ValueError: If the highlighting, visibility, or lifespan are invalid.
        :raises Exception: If the API call fails or returns a 'Bad API request' error.
        """
        url = self.api_url + "api_post.php"
        user_key = user_key or self.default_user_key

        # Fallback to user defaults, if not explicitly provided.
        if highlighting is None and self.default_highlighting:
            highlighting = self.default_highlighting
        if visibility is None and self.default_visibility:
            visibility = self.default_visibility
        if lifespan is None and self.default_expiration:
            lifespan = self.default_expiration

        # Final fallback defaults
        visibility = visibility or "unlisted"
        lifespan = lifespan or "10M"

        # Validate visibility and lifespan
        if visibility not in VISIBILITY_MAP_STR_TO_INT:
            raise ValueError(f"Invalid visibility: {visibility}")
        if lifespan not in LIFESPAN_OPTIONS:
            raise ValueError(f"Invalid lifespan: {lifespan}")

        private_code = VISIBILITY_MAP_STR_TO_INT[visibility]

        payload = {
            "api_dev_key": self.dev_key,
            "api_option": "paste",
            "api_paste_code": text,
            "api_paste_private": private_code,
            "api_paste_expire_date": lifespan,
        }

        if highlighting:
            if highlighting not in HIGHLIGHTING_OPTIONS:
                raise ValueError(f"Invalid highlighting: {highlighting}")
            payload["api_paste_format"] = highlighting

        if name:
            payload["api_paste_name"] = name

        if folder_key:
            payload["api_folder_key"] = folder_key

        if user_key:
            payload["api_user_key"] = user_key

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Failed to create paste: {response.status_code} - {response.text}"
            )

        full_url = response.text.strip()
        # Typically, an error starts with 'Bad API request'
        if not full_url.startswith("https://pastebin.com/"):
            raise Exception(
                f"API error when creating paste. Response was: {response.text}")

        paste_key = full_url.split("/")[-1]

        # Approximate local calculation of expires_at
        lifespan_to_timedelta = {
            "10M": timedelta(minutes=10),
            "1H": timedelta(hours=1),
            "1D": timedelta(days=1),
            "1W": timedelta(weeks=1),
            "2W": timedelta(weeks=2),
            "1M": timedelta(days=30),
            "6M": timedelta(days=180),
            "1Y": timedelta(days=365),
            "N": None,
        }

        expires_at = None
        if lifespan != "N":
            expires_at = datetime.now(
                tz=timezone.utc) + lifespan_to_timedelta[lifespan]

        return PasteDetails(
            paste_key=paste_key,
            url=full_url,
            title=name,
            size=len(text),
            created_at=datetime.now(tz=timezone.utc),
            expires_at=expires_at,
            visibility=visibility,
            highlighting=highlighting,
            hits=0,
        )

    def delete_paste(self, paste_key: str, user_key: str = None) -> None:
        """
        Delete a paste by its key.

        :param paste_key: The unique key (ID) of the paste to delete.
        :param user_key: The user key to use for the request (defaults to self.default_user_key).
        :raises Exception: If the request fails or Pastebin returns an error.
        """
        url = self.api_url + "api_post.php"
        user_key = user_key or self.default_user_key

        payload = {
            "api_dev_key": self.dev_key,
            "api_user_key": user_key,
            "api_paste_key": paste_key,
            "api_option": "delete",
        }

        response = requests.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Failed to delete paste: {response.status_code} - {response.text}"
            )

        if response.text.strip() != "Paste Removed":
            raise Exception(f"Failed to delete paste: {response.text}")

    def fetch_paste_raw(
        self,
        paste_key: str,
        user_owned: bool = True,
        user_key: str = None
    ) -> str:
        """
        Fetch the raw text of a paste.

        :param paste_key: The unique key (ID) of the paste.
        :param user_owned: If True, fetch using the private API endpoint (requires user key).
        :param user_key: The user key to use (defaults to self.default_user_key).
        :return: The text of the paste.
        :raises Exception: If the request fails or Pastebin returns an error.
        """
        user_key = user_key or self.default_user_key

        if user_owned:
            # Required for private or user-owned pastes.
            url = self.api_url + "api_raw.php"
            data = {
                "api_option": "show_paste",
                "api_dev_key": self.dev_key,
                "api_user_key": user_key,
                "api_paste_key": paste_key,
            }
            response = requests.post(url, data=data)
        else:
            # Public or unlisted can be fetched directly.
            url = self.api_url_raw + paste_key
            response = requests.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch paste: {response.status_code} - {response.text}"
            )

        return response.text

    def user_pastes(self, user_key: str = None, limit: int = 50) -> list:
        """
        List all pastes created by the user.

        :param user_key: The user key to use (defaults to self.default_user_key).
        :param limit: The max number of pastes to fetch (1-1000).
        :return: A list of PasteDetails objects.
        :raises Exception: If the request fails or Pastebin returns an error.
        """
        url = self.api_url + "api_post.php"
        user_key = user_key or self.default_user_key

        payload = {
            "api_option": "list",
            "api_dev_key": self.dev_key,
            "api_user_key": user_key,
            "api_results_limit": limit,
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch user pastes: {response.status_code} - {response.text}"
            )

        if response.text.strip() == "No pastes found.":
            return []

        # Wrap the output in <root> so multiple <paste> tags parse properly
        try:
            root = ET.fromstring(f"<root>{response.text}</root>")
        except ET.ParseError as e:
            raise Exception(f"Failed to parse XML: {e}")

        paste_list = []
        for paste_elem in root.findall("paste"):
            paste_key = paste_elem.find("paste_key").text
            created_ts = int(paste_elem.find("paste_date").text)
            created_at = datetime.fromtimestamp(created_ts, tz=timezone.utc)

            raw_title = paste_elem.find("paste_title").text
            title = raw_title if raw_title else "Untitled"

            size = int(paste_elem.find("paste_size").text)
            expire_ts = int(paste_elem.find("paste_expire_date").text)

            expires_at = (
                None
                if expire_ts == 0
                else datetime.fromtimestamp(expire_ts, tz=timezone.utc)
            )

            visibility_int = int(paste_elem.find("paste_private").text)
            visibility_str = VISIBILITY_MAP_INT_TO_STR.get(
                visibility_int, "public")

            highlighting = paste_elem.find("paste_format_short").text
            url_ = paste_elem.find("paste_url").text
            hits = int(paste_elem.find("paste_hits").text)

            paste_data = PasteDetails(
                paste_key=paste_key,
                url=url_,
                title=title,
                size=size,
                created_at=created_at,
                expires_at=expires_at,
                visibility=visibility_str,
                highlighting=highlighting,
                hits=hits,
            )
            paste_list.append(paste_data)

        return paste_list

    def user_details(self, user_key: str = None) -> "UserDetails":
        """
        Fetch details about the user.

        :param user_key: The user key to use (defaults to self.default_user_key).
        :return: A UserDetails object with the user's info and preferences.
        :raises Exception: If the request fails or Pastebin returns an error.
        """
        url = self.api_url + "api_post.php"
        user_key = user_key or self.default_user_key

        payload = {
            "api_option": "userdetails",
            "api_dev_key": self.dev_key,
            "api_user_key": user_key,
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            raise Exception(
                f"Failed to fetch user details: {response.status_code} - {response.text}"
            )

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            raise Exception(f"Failed to parse user details XML: {e}")

        username = root.find("user_name").text
        default_highlighting = root.find("user_format_short").text
        default_expiration = root.find("user_expiration").text
        avatar_url = root.find("user_avatar_url").text

        visibility_int = int(root.find("user_private").text)  # 0,1,2
        default_visibility = VISIBILITY_MAP_INT_TO_STR.get(
            visibility_int, "public")

        website = root.find("user_website").text
        email = root.find("user_email").text
        location = root.find("user_location").text

        # account_type: 0 = normal, 1 = pro
        account_type_int = int(root.find("user_account_type").text)
        account_type_str = ACCOUNT_TYPE_MAP_INT_TO_STR.get(
            account_type_int, "normal")

        return UserDetails(
            username=username,
            avatar_url=avatar_url,
            default_highlighting=default_highlighting,
            default_expiration=default_expiration,
            default_visibility=default_visibility,
            website=website if website else None,
            email=email if email else None,
            location=location if location else None,
            account_type=account_type_str,
        )
