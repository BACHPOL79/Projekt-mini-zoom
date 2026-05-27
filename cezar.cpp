#include <iostream>

using namespace std;

string szyfruj_cezarem(string tj, int klucz)
{
    string szyfrogram = "";
    char znak;
    for (int i = 0 ; i < tj.length() ; i++)
    {
        znak = tj[i];
        if (znak >= 'a' && znak <='z')
        {
            znak = znak - 97;
            znak = znak + (klucz % 26);
            znak = znak % 26;
            znak = znak + 97;
        }
        szyfrogram = szyfrogram + znak;
    }
    return szyfrogram;
}

string odszyfruj_cezara(string szyfrogram, int klucz)
{
    string tekst = "";
    char znak;
    for (int i = 0 ; i < szyfrogram.length() ; i++)
    {
        znak = szyfrogram[i];
        if (znak >= 'a' && znak <='z')
        {
            znak = znak - 97;
            znak = znak - (klucz % 26) + 26;
            znak = znak % 26;
            znak = znak + 97;
        }
        tekst = tekst + znak;
    }
    return tekst;
}

int main()
{
    int kl=3;
    string szyfr;
    string tekst = "ala ma kota xyz";
    szyfr = szyfruj_cezarem(tekst, kl);
    cout << szyfr << endl;
    cout << odszyfruj_cezara(szyfr, kl);

    return 0;
}
