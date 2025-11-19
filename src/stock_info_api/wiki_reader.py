from urllib.parse import unquote

import wikipedia


class NotDataFoundError(Exception):
    pass


class WikiReader:
    def __init__(self, word: str = None):
        wikipedia.set_lang("ja")
        self.word = word

    @property
    def word(self):
        return self._word

    @word.setter
    def word(self, value):
        self._word = value

    def get_description(self):
        try:
            return wikipedia.summary(self.word, auto_suggest=False)
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Disambiguation error: {e.options}"
        except wikipedia.exceptions.PageError:
            raise NotDataFoundError("Page not found")
        except Exception as e:
            return f"An error occurred: {e}"

    def get_url(self):
        try:
            page = wikipedia.page(self.word, auto_suggest=False)
            url = page.url
            encoded_url = unquote(url)
            return encoded_url
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Disambiguation error: {e.options}"
        except wikipedia.exceptions.PageError:
            raise NotDataFoundError("Page not found")
        except Exception as e:
            return f"An error occurred: {e}"


if __name__ == "__main__":
    word = input("Enter a word to search on Wikipedia: ")
    wiki_reader = WikiReader(word)
    print(wiki_reader.get_summary())
    print(wiki_reader.get_url())
