import wikipedia


def get_wikipedia_summary(word):
    try:
        wikipedia.set_lang("ja")
        page = wikipedia.page(word)
        print(page.url)
        summary = wikipedia.summary(word)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Disambiguation error: {e.options}"
    except wikipedia.exceptions.PageError:
        return "Page not found"
    except Exception as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    word = input("Enter a word to search on Wikipedia: ")
    print(get_wikipedia_summary(word))
