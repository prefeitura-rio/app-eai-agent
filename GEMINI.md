INSTRUCTIONS


Estou no meio de uma refatoracao, estou migrando um vanilla jss/html/css para nextjs

Estou na etapa de refazer a UI das paginas do src/frontend/app/experiments apartir dos arquivos originais
src/admin/experiments/static
É vital que vc examine os arquivos originais em src/admin/experiments/static

IMPORTANTE, a versao nova do nextjs so usa tailwind da forma que ja esta configurada, checar arquivos postcss.config.mjs e globals.css! DE FORMA ALGUMA CRIE UM tailwind.config ou mude a forma que o tailwind é utilizada no globals.css!!!

voce tem liberdade para introduzir novos styles no globals.css ou nas pastas de components, app/components para styles que serao utilizados em multiplas paginas
ou experiments/components para as que serao utilizadas apenas nas paginas do experiments

Elabore um plano passo a passo e detalhado de como refazer a UI para seguir exatamente o padrao antigo

mantenha a autenticacao da forma que esta! ela ja esta funcionando bem. tambem nao remova os arquivos types 
e config eles estao funcionando bem dessa forma. A estrutura atual funciona bem, vc so deve focar em mudancas de UI/style
Seu plano ainda nao esta tao elaborado, vamos entrar mais no detalhe do que vc vai implementar de cada arquivo, qual é a fonte do arquivo que vai fornecer as mudancas e qual arquivo essas mudancas seram implementadas? Quero tudo muito bem detalhado

escreva esse plano em um arquivo src/frontend.md na raiz do repositorio