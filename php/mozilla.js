function getDownloadURLForLanguage(aABCD, aPlatform)
{
  var url = "http://download.mozilla.org/?product=firefox&os=";

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
    break;
  default:
    return "http://www.mozilla.org/products/firefox/all.html";
  }

  return url + "&lang=" + aABCD;
}
