from django.db import migrations


# Data to be inserted into WageIndicatorCountryData table.
WAGE_INDICATOR_DATA = [
    {
        'country_code': 'AL',
        'living_wage_link_national': (
            'https://rrogaime.al/paga/pagat-e-jeteses'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/albania'
        ),
        'minimum_wage_link_national': (
            'https://rrogaime.al/paga/paga-minimale-e-arkivuar'
        ),
    },
    {
        'country_code': 'DZ',
        'living_wage_link_national': (
            'https://rawateb.org/algeria/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/algeria'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/algeria/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'AD',
        'living_wage_link_national': (
            'https://tusalario.org/andorra/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/andorra'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/andorra/salario-minimo'
        ),
    },
    {
        'country_code': 'AO',
        'living_wage_link_national': (
            'https://meusalario.org/angola/salario/salarios-dignos'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/angola'
        ),
        'minimum_wage_link_national': (
            'https://meusalario.org/angola/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'AR',
        'living_wage_link_national': (
            'https://elsalario.com.ar/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/argentina'
        ),
        'minimum_wage_link_national': (
            'https://elsalario.com.ar/Salario/salario-minimo'
        ),
    },
    {
        'country_code': 'AM',
        'living_wage_link_national': (
            'https://mywage.org/armenia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/armenia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/armenia/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'AU',
        'living_wage_link_national': (
            'https://mywage.org/australia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/australia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/australia/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'AT',
        'living_wage_link_national': (
            'https://lohnspiegel.org/osterreich/gehalt/'
            'existenzsichernde-lohne'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/austria'
        ),
        'minimum_wage_link_national': (
            'https://lohnspiegel.org/osterreich/gehalt/mindestlohnsatze'
        ),
    },
    {
        'country_code': 'AZ',
        'living_wage_link_national': (
            'https://qazancim.az/qazanc/yasayis-minimumu'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/azerbaijan'
        ),
        'minimum_wage_link_national': (
            'https://qazancim.az/qazanc/minimal-gelir'
        ),
    },
    {
        'country_code': 'BS',
        'living_wage_link_national': (
            'https://mywage.org/bahamas/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/bahamas'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/bahamas/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'BH',
        'living_wage_link_national': (
            'https://rawateb.org/bahrain/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/bahrain'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/bahrain/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'BD',
        'living_wage_link_national': (
            'https://mywage.org.bd/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'bangladesh/38276-bangladesh'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org.bd/salary/minimum-wage/'
        ),
    },
    {
        'country_code': 'BB',
        'living_wage_link_national': (
            'https://mywage.org/barbados/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/barbados'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/barbados/minimum-wage'
        ),
    },
    {
        'country_code': 'BY',
        'living_wage_link_national': (
            'https://mojazarplata.by/zarabotnaja-plata/'
            'prozhitochneye-minimumy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/belarus'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.by/zarabotnaja-plata/'
            'minimalqnaja-zarplata/minimalqnaja-zarplata'
        ),
    },
    {
        'country_code': 'BE',
        'living_wage_link_national': (
            'https://mijnsalaris.be/loon/leefbaar-loon'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/belgium'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.be/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'BZ',
        'living_wage_link_national': (
            'https://mywage.org/belize/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/belize'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/belize/minimum-wage'
        ),
    },
    {
        'country_code': 'BJ',
        'living_wage_link_national': (
            'https://votresalaire.org/benin/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/benin'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/benin/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'BO',
        'living_wage_link_national': (
            'https://tusalario.org/bolivia/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/bolivia'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/bolivia/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'BA',
        'living_wage_link_national': (
            'https://mojaplata.ba/plata/place-za-zivot'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'bosnia-and-herzegovina'
        ),
        'minimum_wage_link_national': (
            'https://mojaplata.ba/plata/minimalna-plata'
        ),
    },
    {
        'country_code': 'BW',
        'living_wage_link_national': (
            'https://mywage.org/botswana/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/botswana'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/botswana/salary/minimum-wage/'
        ),
    },
    {
        'country_code': 'BR',
        'living_wage_link_national': (
            'https://meusalario.org.br/salario-e-renda/salarios-dignos'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/brazil'
        ),
        'minimum_wage_link_national': (
            'https://meusalario.org.br/salario-e-renda/salario-minimo-1'
        ),
    },
    {
        'country_code': 'BN',
        'living_wage_link_national': (
            'https://gajimu.com/brunei/gaji/upah-layak'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/brunei'
        ),
        'minimum_wage_link_national': (
            'https://gajimu.com/brunei/gaji-minimum'
        ),
    },
    {
        'country_code': 'BG',
        'living_wage_link_national': (
            'https://moiatazaplata.org/zaplata/zhiznen-minimum'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/bulgaria'
        ),
        'minimum_wage_link_national': (
            'https://moiatazaplata.org/zaplata/'
            'minimalna-rabotna-zaplata'
        ),
    },
    {
        'country_code': 'BF',
        'living_wage_link_national': (
            'https://votresalaire.org/burkinafaso/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/burkina-faso'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/burkinafaso/salaire/'
            'salaire-minimum'
        ),
    },
    {
        'country_code': 'BI',
        'living_wage_link_national': (
            'https://votresalaire.bi/salaire/salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/burundi'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.bi/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'CV',
        'living_wage_link_national': (
            'https://meusalario.org/caboverde/salario/salarios-dignos'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/cabo-verde'
        ),
        'minimum_wage_link_national': (
            'https://meusalario.org/caboverde/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'KH',
        'living_wage_link_national': (
            'https://prake.org/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/cambodia-1'
        ),
        'minimum_wage_link_national': (
            'https://www.prake.org/home/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'CM',
        'living_wage_link_national': (
            'https://votresalaire.org/cameroun/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/cameroon'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/cameroun/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'CA',
        'living_wage_link_national': (
            'https://mywage.ca/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/canada'
        ),
        'minimum_wage_link_national': (
            'https://www.mywage.ca/home/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'CF',
        'living_wage_link_national': (
            'https://votresalaire.org/centrafricaine/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'central-african-republic'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/centrafricaine/salaire/'
            'salaire-minimum'
        ),
    },
    {
        'country_code': 'TD',
        'living_wage_link_national': (
            'https://votresalaire.org/tchad/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/chad'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/tchad/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'CL',
        'living_wage_link_national': (
            'https://tusalario.org/chile/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/chile'
        ),
        'minimum_wage_link_national': (
            'https://www.tusalario.org/chile/main/salario/'
            'salario-minimo-m'
        ),
    },
    {
        'country_code': 'CN',
        'living_wage_link_national': (
            'https://wageindicator.cn/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/china-custom'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.cn/salary/minimumwagesinchina'
        ),
    },
    {
        'country_code': 'CO',
        'living_wage_link_national': (
            'https://tusalario.org/colombia/tusalario/'
            'salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/colombia'
        ),
        'minimum_wage_link_national': (
            'https://www.tusalario.org/colombia/Portada/tusalario/'
            'salario-minimo'
        ),
    },
    {
        'country_code': 'CD',
        'living_wage_link_national': (
            'https://votresalaire.org/congo/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/congo'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/congo/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'CG',
        'living_wage_link_national': (
            'https://votresalaire.org/congobrazzaville/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'congo-brazzaville'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/congobrazzaville/salaire/'
            'salaires-minimums'
        ),
    },
    {
        'country_code': 'CR',
        'living_wage_link_national': (
            'https://tusalario.org/costarica/tu-salario/'
            'salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/costa-rica'
        ),
        'minimum_wage_link_national': (
            'https://www.tusalario.org/costarica/portada/tu-salario/'
            'salario-minimo'
        ),
    },
    {
        'country_code': 'CI',
        'living_wage_link_national': (
            'https://votresalaire.org/cotedivoire/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/ivory-coast'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/cotedivoire/salaire/'
            'salaire-minimum'
        ),
    },
    {
        'country_code': 'HR',
        'living_wage_link_national': (
            'https://mojaplaca.org/placa/place-dovoljne-za-zivot'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/croatia'
        ),
        'minimum_wage_link_national': (
            'https://www.mojaplaca.org/glavna-stranica/placa/'
            'minimalne-place'
        ),
    },
    {
        'country_code': 'CU',
        'living_wage_link_national': (
            'https://tusalario.org/cuba/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/cuba'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/cuba/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'CY',
        'living_wage_link_national': (
            'https://mywage.org/cyprus/misthos/apodoxes-diaviosis'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/cyprus'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/cyprus/misthos/katotatoi-misthoi-1'
        ),
    },
    {
        'country_code': 'CZ',
        'living_wage_link_national': (
            'https://mujplat.cz/platy-v-cr/dustojne-mzdy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'czech-republic'
        ),
        'minimum_wage_link_national': (
            'https://mujplat.cz/hlavni-stranka/platy-v-cr/'
            'minimalni-mzda'
        ),
    },
    {
        'country_code': 'DK',
        'living_wage_link_national': (
            'https://lontjek.dk/lon/eksistensminimum'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/labour-laws/'
            'labour-law-around-the-world/minimum-wages-regulations/'
            'minimum-wages-regulations-denmark'
        ),
        'minimum_wage_link_national': (
            'https://lontjek.dk/lon/mindstelon'
        ),
    },
    {
        'country_code': 'DJ',
        'living_wage_link_national': (
            'https://rawateb.org/djibouti/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/djibouti'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/djibouti/minimum-wage'
        ),
    },
    {
        'country_code': 'DO',
        'living_wage_link_national': (
            'https://tusalario.org/republicadominicana/salario/'
            'salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'dominican-republic'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/republicadominicana/salario/'
            'salario-minimo'
        ),
    },
    {
        'country_code': 'EC',
        'living_wage_link_national': (
            'https://tusalario.org/ecuador/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/ecuador'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/ecuador/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'EG',
        'living_wage_link_national': (
            'https://rawateb.org/egypt/salaries/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/egypt'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/egypt/Salaries/minimum-wages'
        ),
    },
    {
        'country_code': 'SV',
        'living_wage_link_national': (
            'https://tusalario.org/elsalvador/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/elsalvador'
        ),
        'minimum_wage_link_national': (
            'https://www.tusalario.org/elsalvador/Portada/salario/'
            'salario-minimo-2'
        ),
    },
    {
        'country_code': 'GQ',
        'living_wage_link_national': (
            'https://tusalario.org/guineaecuatorial/salario/'
            'salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'equatorial-guinea'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/guineaecuatorial/salario-minimo'
        ),
    },
    {
        'country_code': 'ER',
        'living_wage_link_national': (
            'https://rawateb.org/eritrea/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/eritrea'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/eritrea/minimum-wage'
        ),
    },
    {
        'country_code': 'EE',
        'living_wage_link_national': (
            'https://mysalary.ee/tootasu/elatusmiinimum'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/estonia'
        ),
        'minimum_wage_link_national': (
            'https://www.mysalary.ee/avaleht/tootasu/'
            'tootasu-alammaarad'
        ),
    },
    {
        'country_code': 'SZ',
        'living_wage_link_national': (
            'https://mywage.org/eswatini/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/eswatini'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/eswatini/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'ET',
        'living_wage_link_national': (
            'https://mywage.org/ethiopia-am/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/ethiopia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/ethiopia/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'FJ',
        'living_wage_link_national': (
            'https://mywage.org/fiji/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/fiji'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/fiji/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'FI',
        'living_wage_link_national': (
            'https://wageindicator.fi/palkkaus/'
            'toimeentulon-turvaava-palkka'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/labour-laws/'
            'labour-law-around-the-world/minimum-wages-regulations/'
            'minimum-wages-regulations-finland'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.fi/palkkaus/vahimmaispalkat'
        ),
    },
    {
        'country_code': 'FR',
        'living_wage_link_national': (
            'https://votresalaire.fr/salaire/salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/france'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.fr/salaire/salaireminimum'
        ),
    },
    {
        'country_code': 'GA',
        'living_wage_link_national': (
            'https://votresalaire.org/gabon/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/gabon'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/gabon/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'GM',
        'living_wage_link_national': (
            'https://mywage.org/gambia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/gambia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/gambia/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'GE',
        'living_wage_link_national': (
            'https://mywage.ge/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/georgia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.ge/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'DE',
        'living_wage_link_national': (
            'https://wageindicator.de/lohn-gehalt/'
            'existenzsichernde-lohne'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/germany'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.de/lohn-gehalt/mindestloehne'
        ),
    },
    {
        'country_code': 'GH',
        'living_wage_link_national': (
            'https://mywage.org/ghana/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/ghana'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/ghana/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'GR',
        'living_wage_link_national': (
            'https://mywage.gr/salary/apodoxes-diaviosis'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/greece'
        ),
        'minimum_wage_link_national': (
            'https://www.mywage.gr/home/salary/elakhistoi-misthoi'
        ),
    },
    {
        'country_code': 'GT',
        'living_wage_link_national': (
            'https://tusalario.org/guatemala/tu-salario/'
            'salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/guatemala'
        ),
        'minimum_wage_link_national': (
            'https://www.tusalario.org/guatemala/Portada/tu-salario/'
            'salario-minimo'
        ),
    },
    {
        'country_code': 'GN',
        'living_wage_link_national': (
            'https://votresalaire.org/guinee/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/guinee'
        ),
        'minimum_wage_link_national': (
            'https://www.votresalaire.org/guinee/home/salaire/'
            'salaire-minimum-11'
        ),
    },
    {
        'country_code': 'GW',
        'living_wage_link_national': (
            'https://meusalario.org/guinebissau/salario/'
            'salarios-dignos'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'guinea-bissau'
        ),
        'minimum_wage_link_national': (
            'https://meusalario.org/guinebissau/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'GY',
        'living_wage_link_national': (
            'https://mywage.org/guyana/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/guyana'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/guyana/minimum-wage'
        ),
    },
    {
        'country_code': 'HT',
        'living_wage_link_national': (
            'https://votresalaire.org/haiti/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/haiti'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/haiti/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'HN',
        'living_wage_link_national': (
            'https://tusalario.org/honduras/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/honduras'
        ),
        'minimum_wage_link_national': (
            'https://www.tusalario.org/honduras/portada/salario/'
            'salario-minimo'
        ),
    },
    {
        'country_code': 'HK',
        'living_wage_link_national': (
            'https://wageindicator.hk/5de58d44/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/hongkong'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.hk/minimum-wage'
        ),
    },
    {
        'country_code': 'HU',
        'living_wage_link_national': (
            'https://berbarometer.hu/munkaber/'
            'megelhetest-biztosito-berek'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/hungary'
        ),
        'minimum_wage_link_national': (
            'https://www.berbarometer.hu/main/munkaber/minimalber'
        ),
    },
    {
        'country_code': 'IN',
        'living_wage_link_national': (
            'https://paycheck.in/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/india'
        ),
        'minimum_wage_link_national': (
            'https://paycheck.in/salary/minimumwages'
        ),
    },
    {
        'country_code': 'ID',
        'living_wage_link_national': (
            'https://gajimu.com/garment/salaries-in-garment/'
            'living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/indonesia'
        ),
        'minimum_wage_link_national': (
            'https://www.gajimu.com/main/gaji/gaji-minimum'
        ),
    },
    {
        'country_code': 'IR',
        'living_wage_link_national': (
            'https://mywage.org/iran/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/iran'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/iran/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'IQ',
        'living_wage_link_national': (
            'https://rawateb.org/iraq/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/iraq'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/iraq/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'IE',
        'living_wage_link_national': (
            'https://mywage.org/ireland/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/ireland'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/ireland/salary/'
            'minimum-wage-in-ireland-with-effect-from-july-1-20155'
        ),
    },
    {
        'country_code': 'IL',
        'living_wage_link_national': (
            'https://mywage.org/israel/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/israel'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/israel/minimum-wages'
        ),
    },
    {
        'country_code': 'IT',
        'living_wage_link_national': (
            'https://iltuosalario.it/stipendio/salari-di-sussistenza'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/italy'
        ),
        'minimum_wage_link_national': (
            'https://iltuosalario.it/stipendio/salariominimo'
        ),
    },
    {
        'country_code': 'JM',
        'living_wage_link_national': (
            'https://mywage.org/jamaica/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/jamaica'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/jamaica/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'JP',
        'living_wage_link_national': (
            'https://kyuryocheck.jp/kyuryo/seikatsu-chingin'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/japan'
        ),
        'minimum_wage_link_national': (
            'https://kyuryocheck.jp/home/kyuryo/Saiteichingin'
        ),
    },
    {
        'country_code': 'JO',
        'living_wage_link_national': (
            'https://rawateb.org/jordan/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/jordan'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/jordan/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'KZ',
        'living_wage_link_national': (
            'https://mojazarplata.kz/zarabotnaja-plata/'
            'prozhitochneye-minimumy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/kazakhstan'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.kz/main/zarabotnaja-plata/'
            'minimalqnaja-zarplata-Kazakhstann'
        ),
    },
    {
        'country_code': 'KE',
        'living_wage_link_national': (
            'https://mywage.org/kenya/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/kenya'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/kenya/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'XK',
        'living_wage_link_national': (
            'https://mywage.org/kosovo/paga/pagat-e-jeteses'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/kosovo'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/kosovo/paga/paga-minimale-e-arkivuar'
        ),
    },
    {
        'country_code': 'KW',
        'living_wage_link_national': (
            'https://rawateb.org/kuwait/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/kuwait'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/kuwait/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'KG',
        'living_wage_link_national': (
            'https://mojazarplata.org/kyrgyzstan/zarabotok/'
            'prozhitochneye-minimumy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/kyrgyzstan'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.org/kyrgyzstan/'
            'minimalnaya-zarabotnaya-plataa'
        ),
    },
    {
        'country_code': 'LA',
        'living_wage_link_national': (
            'https://mywage.org/laos/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/laos'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/laos/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'LV',
        'living_wage_link_national': (
            'https://mysalary.lv/jusu-alga/iztikas-minimums'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/lativa'
        ),
        'minimum_wage_link_national': (
            'https://mysalary.lv/jusu-alga/minimala-darba'
        ),
    },
    {
        'country_code': 'LB',
        'living_wage_link_national': (
            'https://rawateb.org/lebanon/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/lebanon'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/lebanon/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'LS',
        'living_wage_link_national': (
            'https://mywage.org/lesotho/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/lesotho'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/lesotho/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'LR',
        'living_wage_link_national': (
            'https://mywage.org/liberia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/liberia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/liberia/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'LT',
        'living_wage_link_national': (
            'https://mysalary.lt/atlyginimas/'
            'pragyvenima-uztikrinantys-darbo-uzmokesciai'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/lithuania'
        ),
        'minimum_wage_link_national': (
            'https://www.mysalary.lt/pagrindinis/atlyginimas/'
            'minimalusis-darbo'
        ),
    },
    {
        'country_code': 'LU',
        'living_wage_link_national': (
            'https://lohnspiegel.lu/lohn-gehalt/'
            'existenzsichernde-lohne'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/luxemburg'
        ),
        'minimum_wage_link_national': (
            'https://www.lohnspiegel.lu/home/lohn-gehalt/'
            'salaire-minimum'
        ),
    },
    {
        'country_code': 'MO',
        'living_wage_link_national': (
            'https://mywage.org/macao/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/macao'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.org/salary/minimum-wage/macao'
        ),
    },
    {
        'country_code': 'MG',
        'living_wage_link_national': (
            'https://votresalaire.org/madagascar/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/madagascar'
        ),
        'minimum_wage_link_national': (
            'https://www.votresalaire.org/madagascar/home/salaire/'
            'salaire-minimum'
        ),
    },
    {
        'country_code': 'MW',
        'living_wage_link_national': (
            'https://mywage.org/malawi/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/malawi'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/malawi/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'MY',
        'living_wage_link_national': (
            'https://gajimu.my/pendapatan/upah-layak'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/malaysia'
        ),
        'minimum_wage_link_national': (
            'https://gajimu.my/pendapatan/gaji-minimum'
        ),
    },
    {
        'country_code': 'ML',
        'living_wage_link_national': (
            'https://votresalaire.org/mali/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/mali'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/mali/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'MT',
        'living_wage_link_national': (
            'https://mywage.org/malta/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/malta'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/malta/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'MR',
        'living_wage_link_national': (
            'https://rawateb.org/mauritania/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/mauritania'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/mauritania/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'MU',
        'living_wage_link_national': (
            'https://mywage.org/mauritius/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/mauritius'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/mauritius/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'MX',
        'living_wage_link_national': (
            'https://misalario.org/tu-salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/mexico'
        ),
        'minimum_wage_link_national': (
            'https://www.misalario.org/main/tu-salario/salario-minimo'
        ),
    },
    {
        'country_code': 'MD',
        'living_wage_link_national': (
            'https://salariulmeu.org/moldova/salariu/'
            'salarii-pentru-un-trai-decent'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/moldova'
        ),
        'minimum_wage_link_national': (
            'https://salariulmeu.org/moldova/salariu/salariul-minim'
        ),
    },
    {
        'country_code': 'MC',
        'living_wage_link_national': (
            'https://votresalaire.org/monaco/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/monaco'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/monaco/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'MN',
        'living_wage_link_national': (
            'https://mysalary.mn/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/mongolia-1'
        ),
        'minimum_wage_link_national': (
            'https://mysalary.mn/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'ME',
        'living_wage_link_national': (
            'https://mojazarada.me/plata/'
            'minimalni-egzistencijalni-prihodi'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/montenegro'
        ),
        'minimum_wage_link_national': (
            'https://mojazarada.me/plata/minimalna-zarada-crna-gora'
        ),
    },
    {
        'country_code': 'MA',
        'living_wage_link_national': (
            'https://rawateb.org/morocco/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/morocco'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/morocco/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'MZ',
        'living_wage_link_national': (
            'https://meusalario.org/mocambique/salario/salarios-dignos'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/mozambique'
        ),
        'minimum_wage_link_national': (
            'https://www.meusalario.org/mocambique/main/salario/'
            'salario-minimo'
        ),
    },
    {
        'country_code': 'MM',
        'living_wage_link_national': (
            'https://mywage.org/myanmar/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/myanmar'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/myanmar/salary/minimum-wages-myanmar'
        ),
    },
    {
        'country_code': 'NA',
        'living_wage_link_national': (
            'https://mywage.org/namibia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/namibia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/namibia/salary/minimum-wage/'
        ),
    },
    {
        'country_code': 'NP',
        'living_wage_link_national': (
            'https://mywage.org/nepal/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/nepal'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/nepal/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'NL',
        'living_wage_link_national': (
            'https://loonwijzer.nl/salaris/leefbaar-loon'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/netherlands'
        ),
        'minimum_wage_link_national': (
            'https://loonwijzer.nl/salaris/minimumloon-check'
        ),
    },
    {
        'country_code': 'NZ',
        'living_wage_link_national': (
            'https://mywage.co.nz/salaries/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/new-zealand'
        ),
        'minimum_wage_link_national': (
            'https://mywage.co.nz/salaries/minimum-wage'
        ),
    },
    {
        'country_code': 'NI',
        'living_wage_link_national': (
            'https://tusalario.org/nicaragua/tu-salario/'
            'salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/nicaragua'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/nicaragua/tu-salario/salario-minimo'
        ),
    },
    {
        'country_code': 'NE',
        'living_wage_link_national': (
            'https://votresalaire.org/niger/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/niger'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/niger/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'NG',
        'living_wage_link_national': (
            'https://mywage.ng/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/nigeria'
        ),
        'minimum_wage_link_national': (
            'https://mywage.ng/salary/minimum-wage-1'
        ),
    },
    {
        'country_code': 'MK',
        'living_wage_link_national': (
            'https://mojataplata.mk/paga/pagat-e-jeteses'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'north-macedonia'
        ),
        'minimum_wage_link_national': (
            'https://mojataplata.mk/paga/paga-minimale-e-arkivuar'
        ),
    },
    {
        'country_code': 'NO',
        'living_wage_link_national': (
            'https://wageindicator.no/lonn/levelonn'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/norway'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.no/lonn/minstelonn'
        ),
    },
    {
        'country_code': 'OM',
        'living_wage_link_national': (
            'https://rawateb.org/oman/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/oman'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/oman/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'PK',
        'living_wage_link_national': (
            'https://paycheck.pk/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/pakistan'
        ),
        'minimum_wage_link_national': (
            'https://paycheck.pk/salary/minimum-wages/'
        ),
    },
    {
        'country_code': 'PS',
        'living_wage_link_national': (
            'https://rawateb.org/palestine/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/palestine'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/palestine/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'PA',
        'living_wage_link_national': (
            'https://tusalario.org/panama/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/panama'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/panama/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'PG',
        'living_wage_link_national': (
            'https://mywage.org/png/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'papua-new-guinea'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/png/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'PY',
        'living_wage_link_national': (
            'https://tusalario.org/paraguay/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/paraguay'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/paraguay/salario/salario-minimo-1'
        ),
    },
    {
        'country_code': 'PE',
        'living_wage_link_national': (
            'https://tusalario.org/peru/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/peru'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/peru/salario/remuneracion-minima'
        ),
    },
    {
        'country_code': 'PH',
        'living_wage_link_national': (
            'https://mywage.org/philippines/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/philippines'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/philippines/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'PL',
        'living_wage_link_national': (
            'https://twojezarobki.com/wynagrodzenia/'
            'placa-wystarczajaca-na-utrzymanie'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/poland'
        ),
        'minimum_wage_link_national': (
            'https://twojezarobki.com/wynagrodzenia/placa-minimalna'
        ),
    },
    {
        'country_code': 'PT',
        'living_wage_link_national': (
            'https://meusalario.pt/salario/salarios-dignos'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/portugal'
        ),
        'minimum_wage_link_national': (
            'https://meusalario.pt/salario/salariominimo'
        ),
    },
    {
        'country_code': 'PR',
        'living_wage_link_national': (
            'https://tusalario.org/puertorico/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/puerto-rico'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/puertorico/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'QA',
        'living_wage_link_national': (
            'https://rawateb.org/qatar/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/qatar'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/qatar/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'RO',
        'living_wage_link_national': (
            'https://salariulmeu.org/romania/salariu/'
            'salarii-pentru-un-trai-decent'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/romania'
        ),
        'minimum_wage_link_national': (
            'https://salariulmeu.org/romania/salariu/salariuminim'
        ),
    },
    {
        'country_code': 'RU',
        'living_wage_link_national': (
            'https://mojazarplata.ru/zarabotok/prozhitochneye-minimumy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/russia'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.ru/zarabotok/minimalqnaja-zarplata'
        ),
    },
    {
        'country_code': 'RW',
        'living_wage_link_national': (
            'https://mywage.org/rwanda/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/rwanda'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/rwanda/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'ST',
        'living_wage_link_national': (
            'https://meusalario.org/saotomeeprincipe/salario/'
            'salarios-dignoss'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'sao-tome-and-principe'
        ),
        'minimum_wage_link_national': (
            'https://meusalario.org/saotomeeprincipe/salario-minimo'
        ),
    },
    {
        'country_code': 'SA',
        'living_wage_link_national': (
            'https://rawateb.org/saudiarabia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/saudi-arabia'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/saudiarabia/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'SN',
        'living_wage_link_national': (
            'https://votresalaire.org/senegal/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/senegal'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/senegal/salaire/salaire-minimum'
        ),
    },
    {
        'country_code': 'RS',
        'living_wage_link_national': (
            'https://mojazarada.rs/plata/'
            'minimalni-egzistencijalni-prihodi'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/serbia'
        ),
        'minimum_wage_link_national': (
            'https://mojazarada.rs/plata/minimalna-zarada'
        ),
    },
    {
        'country_code': 'SL',
        'living_wage_link_national': (
            'https://mywage.org/sierraleone/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/sierra-leone'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/sierraleone/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'SG',
        'living_wage_link_national': (
            'https://mywage.org/singapore-zh/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/singapore'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/singapore-zh/minimum-wage'
        ),
    },
    {
        'country_code': 'SK',
        'living_wage_link_national': (
            'https://mojplat.sk/platy-na-slovensku/zivotne-minimum'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/slovakia'
        ),
        'minimum_wage_link_national': (
            'https://mojplat.sk/platy-na-slovensku/minimalna-mzda/'
            'narodna-minimalna-mzda'
        ),
    },
    {
        'country_code': 'SI',
        'living_wage_link_national': (
            'https://mojaplaca.si/placi/place-zadostne-za-prezivljanje'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/slovenia'
        ),
        'minimum_wage_link_national': (
            'https://mojaplaca.si/placi/minimalne-place'
        ),
    },
    {
        'country_code': 'SO',
        'living_wage_link_national': (
            'https://mywage.org/somalia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/somalia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/somalia/mushahar/mushaharka-ugu-yar'
        ),
    },
    {
        'country_code': 'ZA',
        'living_wage_link_national': (
            'https://mywage.co.za/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/south-africa'
        ),
        'minimum_wage_link_national': (
            'https://mywage.co.za/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'KR',
        'living_wage_link_national': (
            'https://mywage.org/korea/imgeum/saenghwal-imgeum'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/south-korea'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/korea/imgeum/choejeo-imgeum'
        ),
    },
    {
        'country_code': 'SS',
        'living_wage_link_national': (
            'https://mywage.org/southsudan/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/south-sudan'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/southsudan/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'ES',
        'living_wage_link_national': (
            'https://tusalario.es/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/spain'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.es/salario/minimo'
        ),
    },
    {
        'country_code': 'LK',
        'living_wage_link_national': (
            'https://salary.lk/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/sri-lanka'
        ),
        'minimum_wage_link_national': (
            'https://salary.lk/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'SD',
        'living_wage_link_national': (
            'https://rawateb.org/sudan/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/sudan'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/sudan/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'SR',
        'living_wage_link_national': (
            'https://loonwijzer.org/suriname/loon/leefbaar-loon'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/suriname'
        ),
        'minimum_wage_link_national': (
            'https://loonwijzer.org/suriname/loon/minimum-loon'
        ),
    },
    {
        'country_code': 'SE',
        'living_wage_link_national': (
            'https://lonecheck.se/loene/levnadsloner'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/sweden'
        ),
        'minimum_wage_link_national': (
            'https://lonecheck.se/loene/minimilon'
        ),
    },
    {
        'country_code': 'CH',
        'living_wage_link_national': (
            'https://votresalaire.org/suisse/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/switzerland'
        ),
        'minimum_wage_link_national': (
            'https://lohnspiegel.org/schweiz/lohn-gehalt/mindestlohn'
        ),
    },
    {
        'country_code': 'SY',
        'living_wage_link_national': (
            'https://rawateb.org/syria/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/syria'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/syria/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'TW',
        'living_wage_link_national': (
            'https://wageindicator.tw/5de58d44/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/taiwan'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.tw/minimum-wage'
        ),
    },
    {
        'country_code': 'TJ',
        'living_wage_link_national': (
            'https://mojazarplata.org/tajikistan/zarabotok/'
            'prozhitochneye-minimumy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/tajikistan'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.org/tajikistan/'
            'minimalnaya-zarabotnaya-plata'
        ),
    },
    {
        'country_code': 'TZ',
        'living_wage_link_national': (
            'https://africapay.org/tanzania/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/tanzania'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/tanzania/income/minimum-wage'
        ),
    },
    {
        'country_code': 'TH',
        'living_wage_link_national': (
            'https://mywage.org/thailand/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/thailand'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/thailand/minimum-wages'
        ),
    },
    {
        'country_code': 'TG',
        'living_wage_link_national': (
            'https://votresalaire.org/togo/salaire/'
            'salaires-minimums-vitaux'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/togo'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/togo/salaire/'
            'salaire-minimum-tarifs'
        ),
    },
    {
        'country_code': 'TT',
        'living_wage_link_national': (
            'https://mywage.org/trinidadandtobago/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'trinidad-and-tobago'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/trinidadandtobago/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'TN',
        'living_wage_link_national': (
            'https://rawateb.org/tunisia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/tunisia'
        ),
        'minimum_wage_link_national': (
            'https://votresalaire.org/tunisie/salaire/'
            'salaire-minimum-1'
        ),
    },
    {
        'country_code': 'TR',
        'living_wage_link_national': (
            'https://maascetveli.org/maas/adil-yasam-ucreti'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/turkey'
        ),
        'minimum_wage_link_national': (
            'https://maascetveli.org/maas/asgari-ucretler'
        ),
    },
    {
        'country_code': 'UG',
        'living_wage_link_national': (
            'https://mywage.org/uganda/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/uganda'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/uganda/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'UA',
        'living_wage_link_national': (
            'https://mojazarplata.com.ua/ua/zarobitok/'
            'prozhytkovyy-minimalnyy-ryven-zarobitnoyi-platy'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/ukraine'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.com.ua/ua/zarobitok/'
            'minimalqna-zarplata'
        ),
    },
    {
        'country_code': 'AE',
        'living_wage_link_national': (
            'https://rawateb.org/uae/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'united-arab-emirates'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/uae/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'GB',
        'living_wage_link_national': (
            'https://wageindicator.co.uk/pay/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'united-kingdom'
        ),
        'minimum_wage_link_national': (
            'https://wageindicator.co.uk/pay/minimum-wages'
        ),
    },
    {
        'country_code': 'US',
        'living_wage_link_national': (
            'https://paywizard.org/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/'
            'united-states-of-america'
        ),
        'minimum_wage_link_national': (
            'https://paywizard.org/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'UY',
        'living_wage_link_national': (
            'https://tusalario.org/uruguay/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/uruguay'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/uruguay/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'UZ',
        'living_wage_link_national': (
            'https://mojazarplata.org/uzbekistan/ish-haqi/'
            'yashash-uchun-minimal-ish-haqlari'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/uzbekistan'
        ),
        'minimum_wage_link_national': (
            'https://mojazarplata.org/uzbekistan/minimal-ish-haqi'
        ),
    },
    {
        'country_code': 'VE',
        'living_wage_link_national': (
            'https://tusalario.org/venezuela/salario/salarios-vitales'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/venezuela'
        ),
        'minimum_wage_link_national': (
            'https://tusalario.org/venezuela/salario/salario-minimo'
        ),
    },
    {
        'country_code': 'VN',
        'living_wage_link_national': (
            'https://luong.com.vn/tien-luong/'
            'luong-sinh-hoat-toi-thieu'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/vietnam'
        ),
        'minimum_wage_link_national': (
            'https://luong.com.vn/tien-luong/luong-toi-thieu-rate'
        ),
    },
    {
        'country_code': 'YE',
        'living_wage_link_national': (
            'https://rawateb.org/yemen/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/yemen'
        ),
        'minimum_wage_link_national': (
            'https://rawateb.org/yemen/salary/minimum-wages'
        ),
    },
    {
        'country_code': 'ZM',
        'living_wage_link_national': (
            'https://mywage.org/zambia/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/zambia'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/zambia/salary/minimum-wage'
        ),
    },
    {
        'country_code': 'ZW',
        'living_wage_link_national': (
            'https://mywage.org/zimbabwe/salary/living-wages'
        ),
        'minimum_wage_link_english': (
            'https://wageindicator.org/salary/minimum-wage/zimbabwe'
        ),
        'minimum_wage_link_national': (
            'https://mywage.org/zimbabwe/salary/minimum-wage'
        ),
    },
]

WAGE_INDICATOR_LINK_TEXT_DATA = [
    {
        'link_type': 'living_wage_link_national',
        'display_text': (
            'Living Wage in national language'
        ),
    },
    {
        'link_type': 'minimum_wage_link_english',
        'display_text': (
            'Minimum Wage in English'
        ),
    },
    {
        'link_type': 'minimum_wage_link_national',
        'display_text': (
            'Minimum Wage in national language'
        ),
    },
]


def populate_wage_indicator_data(apps, schema_editor):
    '''
    Populate both WageIndicatorCountryData and WageIndicatorLinkTextConfig
    tables with initial data.
    '''
    WageIndicatorCountryData = apps.get_model(
        'api', 'WageIndicatorCountryData'
    )
    WageIndicatorLinkTextConfig = apps.get_model(
        'api', 'WageIndicatorLinkTextConfig'
    )

    # Bulk create all country data records.
    wage_data_objects = [
        WageIndicatorCountryData(**data)
        for data in WAGE_INDICATOR_DATA
    ]

    WageIndicatorCountryData.objects.bulk_create(
        wage_data_objects,
        batch_size=100
    )

    link_text_configs = [
        WageIndicatorLinkTextConfig(**data)
        for data in WAGE_INDICATOR_LINK_TEXT_DATA
    ]

    WageIndicatorLinkTextConfig.objects.bulk_create(link_text_configs)


def clean_wage_indicator_data(apps, schema_editor):
    '''
    Clean both WageIndicatorCountryData and WageIndicatorLinkTextConfig tables.
    '''
    WageIndicatorCountryData = apps.get_model(
        'api', 'WageIndicatorCountryData'
    )
    WageIndicatorLinkTextConfig = apps.get_model(
        'api', 'WageIndicatorLinkTextConfig'
    )

    WageIndicatorLinkTextConfig.objects.all().delete()
    WageIndicatorCountryData.objects.all().delete()


class Migration(migrations.Migration):
    '''
    This migration populates the WageIndicatorCountryData and
    WageIndicatorLinkTextConfig tables with initial data.
    '''

    dependencies = [
        ('api', '0192_create_wage_indicator_models'),
    ]

    operations = [
        migrations.RunPython(
            populate_wage_indicator_data,
            clean_wage_indicator_data
        ),
    ]
