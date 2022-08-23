from common.botmain import BotMain
from common.jobwithquery import JobWithQuery

NAME = "Rename backlinks"
DESCRIPTION = "Rename backlinks of a redirect to the redirect target"
DRY_RUN = False


class RenameWithBacklinks(JobWithQuery):

    def __init__(self):
        super().__init__()

    def process(self, article):
        page = self.client.pages[article]
        print("Procesando " + page.name)
        target = page.redirects_to()
        if not target:
            # not a redirect
            return
        for referrer in page.backlinks():
            oldtext = referrer.text()
            wikitext = oldtext.replace(f"Usuario discusión:Dark delegation/", f"Usuario discusión:DD/")
            if oldtext != wikitext:
                print(f"Actualizar redirección por destino, cambiando {page.name} por {target.name} en {referrer.name}")
                if not DRY_RUN:
                    referrer.edit(wikitext,
                                  summary=f"Actualizar redirección, cambiar Usuario:Dark delegation/* por Usuario:DD/*")

    @property
    def querybuilder_title(self):
        # Ideally you would add in your JSON the translations and use this:
        # return self.lang.t("scripts.yourscriptname.name")
        # If you feel lazy, hardcode the value
        return "Renombrar referencias"


# Don't delete this line or your script won't start
BotMain(DESCRIPTION).start(RenameWithBacklinks())
