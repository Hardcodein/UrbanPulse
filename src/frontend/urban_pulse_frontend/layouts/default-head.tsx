import Head from 'next/head'

export function DefaultHead(): JSX.Element {
  return (
    <Head>
      <meta
        itemProp="description"
        name="description"
        content="Карта для оценки доступности социальной инфраструктуры и плотности населения"
      />
      <meta
        itemProp="keywords"
        name="keywords"
        content="UrbanPulse, карта, экология, социальная инфраструктура, рельеф, карта высот, карта застройки, плотность застройки, Ростов-на-Дону"
      />
      <title>
        UrbanPulse. Карта социальной инфраструктуры и плотности населения городов.
      </title>
    </Head>
  )
}
