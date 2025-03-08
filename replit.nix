{ pkgs }:
{
  deps = [
    pkgs.python39Full
    pkgs.chromium
    pkgs.chromedriver
    pkgs.libnss
    pkgs.gconf
    pkgs.libasound
    pkgs.gtk3
    pkgs.xorg.libX11
  ];
}
