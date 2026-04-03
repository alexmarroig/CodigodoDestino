export type BrazilCityOption = {
  id: string
  label: string
  timezone: string
  lat: number
  lon: number
}

export const DEFAULT_BRAZIL_CITY_ID = 'sao_paulo'

export const BRAZIL_CITY_OPTIONS: BrazilCityOption[] = [
  { id: 'aracaju', label: 'Aracaju, SE', timezone: 'America/Maceio', lat: -10.9472, lon: -37.0731 },
  { id: 'belem', label: 'Belem, PA', timezone: 'America/Belem', lat: -1.4558, lon: -48.4902 },
  { id: 'belo_horizonte', label: 'Belo Horizonte, MG', timezone: 'America/Sao_Paulo', lat: -19.9167, lon: -43.9345 },
  { id: 'boa_vista', label: 'Boa Vista, RR', timezone: 'America/Boa_Vista', lat: 2.8235, lon: -60.6753 },
  { id: 'brasilia', label: 'Brasilia, DF', timezone: 'America/Sao_Paulo', lat: -15.7939, lon: -47.8828 },
  { id: 'campinas', label: 'Campinas, SP', timezone: 'America/Sao_Paulo', lat: -22.9099, lon: -47.0626 },
  { id: 'campo_grande', label: 'Campo Grande, MS', timezone: 'America/Campo_Grande', lat: -20.4697, lon: -54.6201 },
  { id: 'cuiaba', label: 'Cuiaba, MT', timezone: 'America/Cuiaba', lat: -15.6014, lon: -56.0979 },
  { id: 'curitiba', label: 'Curitiba, PR', timezone: 'America/Sao_Paulo', lat: -25.4284, lon: -49.2733 },
  { id: 'florianopolis', label: 'Florianopolis, SC', timezone: 'America/Sao_Paulo', lat: -27.5949, lon: -48.5482 },
  { id: 'fortaleza', label: 'Fortaleza, CE', timezone: 'America/Fortaleza', lat: -3.7319, lon: -38.5267 },
  { id: 'goiania', label: 'Goiania, GO', timezone: 'America/Sao_Paulo', lat: -16.6869, lon: -49.2648 },
  { id: 'joao_pessoa', label: 'Joao Pessoa, PB', timezone: 'America/Recife', lat: -7.1195, lon: -34.845 },
  { id: 'maceio', label: 'Maceio, AL', timezone: 'America/Maceio', lat: -9.6498, lon: -35.7089 },
  { id: 'macapa', label: 'Macapa, AP', timezone: 'America/Belem', lat: 0.0349, lon: -51.0694 },
  { id: 'manaus', label: 'Manaus, AM', timezone: 'America/Manaus', lat: -3.119, lon: -60.0217 },
  { id: 'natal', label: 'Natal, RN', timezone: 'America/Recife', lat: -5.7945, lon: -35.211 },
  { id: 'porto_alegre', label: 'Porto Alegre, RS', timezone: 'America/Sao_Paulo', lat: -30.0346, lon: -51.2177 },
  { id: 'porto_velho', label: 'Porto Velho, RO', timezone: 'America/Porto_Velho', lat: -8.7608, lon: -63.8999 },
  { id: 'recife', label: 'Recife, PE', timezone: 'America/Recife', lat: -8.0476, lon: -34.877 },
  { id: 'rio_branco', label: 'Rio Branco, AC', timezone: 'America/Rio_Branco', lat: -9.9747, lon: -67.8243 },
  { id: 'rio_de_janeiro', label: 'Rio de Janeiro, RJ', timezone: 'America/Sao_Paulo', lat: -22.9068, lon: -43.1729 },
  { id: 'salvador', label: 'Salvador, BA', timezone: 'America/Bahia', lat: -12.9777, lon: -38.5016 },
  { id: 'santos', label: 'Santos, SP', timezone: 'America/Sao_Paulo', lat: -23.9608, lon: -46.3336 },
  { id: 'sao_luis', label: 'Sao Luis, MA', timezone: 'America/Belem', lat: -2.53, lon: -44.2958 },
  { id: 'sao_paulo', label: 'Sao Paulo, SP', timezone: 'America/Sao_Paulo', lat: -23.5505, lon: -46.6333 },
  { id: 'teresina', label: 'Teresina, PI', timezone: 'America/Fortaleza', lat: -5.0892, lon: -42.8019 },
  { id: 'vitoria', label: 'Vitoria, ES', timezone: 'America/Sao_Paulo', lat: -20.3155, lon: -40.3128 },
]
