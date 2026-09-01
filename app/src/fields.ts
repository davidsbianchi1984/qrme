/** What a profile works in, in every language the product speaks.
 *
 *     asked     translate the field names
 *     mattered  translate them without breaking the guard that counts them
 *
 * Its own file, and that is the whole point of the file.
 *
 * `tr("ind." + key)` was the obvious first move and it is the trap this
 * codebase keeps walking into: a lookup assembled from a variable is
 * invisible to `test_the_stranger_has_a_language_too`, so thirty-four
 * keys would have been translated into ten languages, shipped, and
 * reported by the guard as not existing.
 *
 * The second move — the table inside `l10n.ts` — broke the guard from
 * the other end. It reads that file for `"key": { en: … }` entries and
 * flags any nothing calls `tr()` on, so a closed vocabulary reached
 * through a helper looked like thirty-four translated strings nobody
 * uses. The guard was right both times.
 *
 * So the vocabulary lives here instead. `l10n.ts` stays exactly what the
 * guard believes it is — the file of `tr()` keys — and a table the
 * product owns and reaches through one helper is a different thing,
 * kept in a different place, counted by nobody's rule for the other.
 *
 * A field this table has not heard of falls back to the key with its
 * underscores opened out: wrong-looking rather than blank, which is the
 * right failure for a vocabulary that can grow.
 */
export const FIELDS: Record<string, Record<string, string>> = {
  "adult": { en: "Adult", es: "Para adultos", fr: "Pour adultes", de: "Erwachsene", pt: "Adulto", it: "Per adulti", ja: "アダルト", zh: "成人", hi: "वयस्क", ar: "للبالغين", },
  "aerospace": { en: "Aerospace", es: "Aeroespacial", fr: "Aérospatiale", de: "Luft- und Raumfahrt", pt: "Aeroespacial", it: "Aerospaziale", ja: "航空宇宙", zh: "航空航天", hi: "एयरोस्पेस", ar: "الفضاء الجوي", },
  "agriculture": { en: "Agriculture", es: "Agricultura", fr: "Agriculture", de: "Landwirtschaft", pt: "Agricultura", it: "Agricoltura", ja: "農業", zh: "农业", hi: "कृषि", ar: "الزراعة", },
  "arts_design": { en: "Arts and design", es: "Arte y diseño", fr: "Arts et design", de: "Kunst und Design", pt: "Arte e design", it: "Arte e design", ja: "アートとデザイン", zh: "艺术与设计", hi: "कला और डिज़ाइन", ar: "الفنون والتصميم", },
  "automotive": { en: "Automotive", es: "Automoción", fr: "Automobile", de: "Automobil", pt: "Automotivo", it: "Automotive", ja: "自動車", zh: "汽车", hi: "ऑटोमोटिव", ar: "السيارات", },
  "construction": { en: "Construction", es: "Construcción", fr: "Construction", de: "Bauwesen", pt: "Construção", it: "Edilizia", ja: "建設", zh: "建筑", hi: "निर्माण", ar: "البناء", },
  "counseling": { en: "Counselling", es: "Orientación", fr: "Accompagnement", de: "Beratung", pt: "Aconselhamento", it: "Counseling", ja: "カウンセリング", zh: "心理咨询", hi: "परामर्श", ar: "الإرشاد", },
  "culinary": { en: "Culinary", es: "Gastronomía", fr: "Cuisine", de: "Kulinarik", pt: "Culinária", it: "Cucina", ja: "料理", zh: "烹饪", hi: "पाक कला", ar: "فنون الطهي", },
  "cybersecurity": { en: "Cybersecurity", es: "Ciberseguridad", fr: "Cybersécurité", de: "Cybersicherheit", pt: "Cibersegurança", it: "Cybersicurezza", ja: "サイバーセキュリティ", zh: "网络安全", hi: "साइबर सुरक्षा", ar: "الأمن السيبراني", },
  "education": { en: "Education", es: "Educación", fr: "Éducation", de: "Bildung", pt: "Educação", it: "Istruzione", ja: "教育", zh: "教育", hi: "शिक्षा", ar: "التعليم", },
  "energy": { en: "Energy", es: "Energía", fr: "Énergie", de: "Energie", pt: "Energia", it: "Energia", ja: "エネルギー", zh: "能源", hi: "ऊर्जा", ar: "الطاقة", },
  "environment": { en: "Environment", es: "Medio ambiente", fr: "Environnement", de: "Umwelt", pt: "Meio ambiente", it: "Ambiente", ja: "環境", zh: "环境", hi: "पर्यावरण", ar: "البيئة", },
  "fashion_beauty": { en: "Fashion and beauty", es: "Moda y belleza", fr: "Mode et beauté", de: "Mode und Schönheit", pt: "Moda e beleza", it: "Moda e bellezza", ja: "ファッションと美容", zh: "时尚与美容", hi: "फ़ैशन और सौंदर्य", ar: "الأزياء والجمال", },
  "finance": { en: "Finance", es: "Finanzas", fr: "Finance", de: "Finanzen", pt: "Finanças", it: "Finanza", ja: "金融", zh: "金融", hi: "वित्त", ar: "التمويل", },
  "government": { en: "Government", es: "Gobierno", fr: "Administration publique", de: "Verwaltung", pt: "Governo", it: "Pubblica amministrazione", ja: "行政", zh: "政府", hi: "सरकार", ar: "الحكومة", },
  "healthcare": { en: "Healthcare", es: "Salud", fr: "Santé", de: "Gesundheit", pt: "Saúde", it: "Sanità", ja: "医療", zh: "医疗", hi: "स्वास्थ्य सेवा", ar: "الرعاية الصحية", },
  "hospitality": { en: "Hospitality", es: "Hostelería", fr: "Hôtellerie", de: "Gastgewerbe", pt: "Hotelaria", it: "Ospitalità", ja: "ホスピタリティ", zh: "酒店业", hi: "आतिथ्य", ar: "الضيافة", },
  "human_resources": { en: "Human resources", es: "Recursos humanos", fr: "Ressources humaines", de: "Personalwesen", pt: "Recursos humanos", it: "Risorse umane", ja: "人事", zh: "人力资源", hi: "मानव संसाधन", ar: "الموارد البشرية", },
  "insurance": { en: "Insurance", es: "Seguros", fr: "Assurance", de: "Versicherung", pt: "Seguros", it: "Assicurazioni", ja: "保険", zh: "保险", hi: "बीमा", ar: "التأمين", },
  "legal": { en: "Legal", es: "Derecho", fr: "Droit", de: "Recht", pt: "Jurídico", it: "Legale", ja: "法務", zh: "法律", hi: "कानूनी", ar: "القانون", },
  "manufacturing": { en: "Manufacturing", es: "Fabricación", fr: "Industrie", de: "Fertigung", pt: "Manufatura", it: "Manifattura", ja: "製造", zh: "制造业", hi: "विनिर्माण", ar: "التصنيع", },
  "marketing": { en: "Marketing", es: "Marketing", fr: "Marketing", de: "Marketing", pt: "Marketing", it: "Marketing", ja: "マーケティング", zh: "市场营销", hi: "मार्केटिंग", ar: "التسويق", },
  "media": { en: "Media", es: "Medios", fr: "Médias", de: "Medien", pt: "Mídia", it: "Media", ja: "メディア", zh: "媒体", hi: "मीडिया", ar: "الإعلام", },
  "mental_health": { en: "Mental health", es: "Salud mental", fr: "Santé mentale", de: "Psychische Gesundheit", pt: "Saúde mental", it: "Salute mentale", ja: "メンタルヘルス", zh: "心理健康", hi: "मानसिक स्वास्थ्य", ar: "الصحة النفسية", },
  "music": { en: "Music", es: "Música", fr: "Musique", de: "Musik", pt: "Música", it: "Musica", ja: "音楽", zh: "音乐", hi: "संगीत", ar: "الموسيقى", },
  "nonprofit": { en: "Nonprofit", es: "Sin ánimo de lucro", fr: "Associatif", de: "Gemeinnützig", pt: "Sem fins lucrativos", it: "No profit", ja: "非営利", zh: "非营利", hi: "गैर-लाभकारी", ar: "غير ربحي", },
  "psychiatry": { en: "Psychiatry", es: "Psiquiatría", fr: "Psychiatrie", de: "Psychiatrie", pt: "Psiquiatria", it: "Psichiatria", ja: "精神医学", zh: "精神病学", hi: "मनोचिकित्सा", ar: "الطب النفسي", },
  "real_estate": { en: "Real estate", es: "Inmobiliaria", fr: "Immobilier", de: "Immobilien", pt: "Imóveis", it: "Immobiliare", ja: "不動産", zh: "房地产", hi: "रियल एस्टेट", ar: "العقارات", },
  "retail": { en: "Retail", es: "Comercio minorista", fr: "Commerce de détail", de: "Einzelhandel", pt: "Varejo", it: "Vendita al dettaglio", ja: "小売", zh: "零售", hi: "खुदरा", ar: "التجزئة", },
  "science": { en: "Science", es: "Ciencia", fr: "Science", de: "Wissenschaft", pt: "Ciência", it: "Scienza", ja: "科学", zh: "科学", hi: "विज्ञान", ar: "العلوم", },
  "sports_fitness": { en: "Sport and fitness", es: "Deporte y fitness", fr: "Sport et fitness", de: "Sport und Fitness", pt: "Esporte e fitness", it: "Sport e fitness", ja: "スポーツとフィットネス", zh: "运动与健身", hi: "खेल और फ़िटनेस", ar: "الرياضة واللياقة", },
  "technology": { en: "Technology", es: "Tecnología", fr: "Technologie", de: "Technologie", pt: "Tecnologia", it: "Tecnologia", ja: "テクノロジー", zh: "科技", hi: "प्रौद्योगिकी", ar: "التقنية", },
  "telecom": { en: "Telecoms", es: "Telecomunicaciones", fr: "Télécoms", de: "Telekommunikation", pt: "Telecomunicações", it: "Telecomunicazioni", ja: "通信", zh: "电信", hi: "दूरसंचार", ar: "الاتصالات", },
  "transportation": { en: "Transport", es: "Transporte", fr: "Transport", de: "Verkehr", pt: "Transporte", it: "Trasporti", ja: "運輸", zh: "交通运输", hi: "परिवहन", ar: "النقل", },
};

export function field(key: string | null | undefined, lang: string): string {
  if (!key) return "";
  const row = FIELDS[key];
  if (!row) return key.replace(/_/g, " ");
  return row[lang] || row.en;
}
