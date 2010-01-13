function getDownloadURLForLanguage(aABCD, aPlatform)
{
  var url = "http://download.mozilla.org/?product=firefox&amp;os=";

  switch (aPlatform) {
  case PLATFORM_WINDOWS:
    url += "win";
    break;
  case PLATFORM_LINUX:
    url += "linux";
    break;
  case PLATFORM_MACOSX:
    url += "osx";
    if (aABCD == "ja-JP")
      aABCD = "ja-JPM";
    if (aABCD == "ja")
      aABCD = "ja-JP-mac";
    break;
  default:
    return "http://www.mozilla.com/" + aABCD + "/firefox/all.html";
  }

  return url + "&amp;lang=" + aABCD;
}
