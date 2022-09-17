# Dinosaur Homepage - Script for ssg

from collections.abc import Callable

from nisshi import Manager


HEADDING_PREFIXES = tuple(f'{"#"*i} ' for i in range(1, 6))
"マークダウンの見出しを作る際、最初に置くやつ。"


class NewPage(Manager.page_cls):
    "色々楽にできるように拡張したPageクラスです。"

    MENTION_PREFIXES = {"@": "＠", "#": "＃", "v#": "🔊"}
    "メンションの最初に置くやつの半角と全角の辞書。"
    for key in list(MENTION_PREFIXES.keys()):
        MENTION_PREFIXES[MENTION_PREFIXES[key]] = MENTION_PREFIXES[key]

    mtn_id = False
    _contents_data = None
    _contents_stack = []

    def make_tree(
        self, data: dict,
        parser: Callable[[str], str]
            = lambda x: x,
        put_id: bool = False
    ) -> str:
        "ツリーを作る。辞書から作れます。"
        put_id_ = lambda k: f' id="{k}"' if put_id else ""
        return "{}{}{}".format("<dl>", "".join(
            "<dt{}>{}</dt><dd>{}</dd>".format(
                put_id_(key), parser(key),
                self.make_tree(value, parser)
                    if isinstance(value, dict)
                    else value
            ) if value else "<span{}>{}</span>".format(
                put_id_(key), parser(key)
            ) for key, value in data.items()
        ), "</dl>")

    def mtn(self, target: str) -> str:
        "メンションを作ります。"
        extend = ""
        if self.mtn_id:
            extend = f' id="{target}"'
        return f'<span class="mention"{extend}>{target}</span>'

    def _collect_contents_data(self, reference: dict, data: dict | None = None) -> dict | str:
        # 再帰を行なって、目次の内容のデータを辞書に入れます。
        # やってることは、`self._contents_stack`にあるデータから、`self.make_tree`用のデータを作ること。
        # 目次データを作ってそこに見出しの内容を入れて、より深い見出しは、新しくその目次データに目次データを作って、そこにその見出しを入れるために再帰すると入った感じ。
        if not self._contents_stack:
            return {}

        data = data or {}

        super_, key = self._contents_stack[0]
        if super_ not in data:
            if super_:
                # ここが呼ばれるということは、h5とかの深いとこから、h3などまで浅くなったということ。
                # 今扱っている目次に入れるべき見出しは、今扱っている目次データに入れれない。
                # なぜなら、今扱っている目次データは、h5とかの深いとこの目次データで、その今扱っている浅い見出しを入れるべき場所ではないからだ。
                # その入れるべき場所は浅いとこにあるため、遡る必要がある。
                # いままでこの関数を呼び出してきた実行されたこの関数達のどこかに、その入れるべき場所を扱っていた関数がいるはずだ。
                # そこまで巻き戻すのは面倒なので、予め`reference`に入れていた目次データの参照で、入れるべき場所である目次データまで瞬間移動する。
                return self._collect_contents_data(reference, reference[super_])
            else:
                data[super_] = {}
        data[super_][key] = {}
        del self._contents_stack[0]

        # 簡単に深いとこから浅いとこまで遡れるように、データの参照を格納しておく。
        if super_ not in reference:
            reference[super_] = data
        if key not in reference:
            reference[key] = data[super_]

        if self._contents_stack:
            return self._collect_contents_data(reference, data)
        else:
            return reference[""][""]

    def collect_contents_data(self) -> dict:
        "`self.make_tree`で使用可能な辞書形式のデータを、ドキュメント内にある見出しから作ります。"
        if self._contents_data is None:
            self._contents_data = self._collect_contents_data({})
        return self._contents_data

    def make_table_of_contents_from_data(self, data: dict) -> str:
        "渡された`self.make_tree`で扱える形式の辞書から、目次を作ります。"
        return '<div id="table_contents">%s</div>' % self.make_tree(
            data, lambda v: f'<a href="#{v}">{v}</a><br>'
        )

    def make_table_of_contents(self) -> str:
        "ドキュメント内にある見出しから目次を作ります。"
        return self.make_table_of_contents_from_data(self.collect_contents_data())

    def on_read_raw(self) -> None:
        "テンプレートの内容(マークダウン)が読み込まれた際に、nisshiにより呼ばれる関数です。"
        # 見出しにIDを割り振る。また、必要に応じて目次データの元を生成する。
        # 目次データの元の形式は、`list[tuple[親の見出しの名前, 見出しの名前]]`で、以下に例を示す。
        # これで作った目次データの元は、`self._contents_stack`に格納されて、`self.collect_contents_data`で使用される。
        """
        ```md
        # h1
        ## h2
        ## h2-2
        ### h3
        ## h2-3
        ### h3
        ```
        ↓
        ```python
        [("", "h1"), ("h1", "h2"), ("h1", "h2-2"), ("h2-2", "h3"), ("h1", "h2-3"), ("h2-3", "h3")]
        ```
        """
        # テンプレートの中に目次を生成するためのものがある場合は、目次データの元を集めるようにする。
        make_contents = "collect_contents_data" in self.template.raw \
            or "make_table_of_contents()" in self.template.raw

        # 見出しにIDを割り振る。
        contents_stack, parents, before = [], [], 0
        for line in self.template.raw.splitlines():
            for i, prefix in enumerate(HEADDING_PREFIXES, 1):
                if line.startswith(prefix):
                    new = line.replace(prefix, '', 1).replace('"', '\\"')
                    self.template.raw = self.template.raw.replace(
                        line, f'<h{i} id="{new}">{new}</h{i}>', 1
                    )

                    if make_contents:
                        # 目次データの元を格納する。
                        if i < before:
                            parents = parents[:before - i]
                        contents_stack.append((parents[-1] if parents else "", new)) # parents.copy())
                        if before < i:
                            parents.append(new)
                        before = i

        if make_contents:
            self._contents_stack = contents_stack