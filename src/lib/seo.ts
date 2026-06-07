export function buildCatSchema(cat: any, url: string) {
  return {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": cat.title,
    "description": cat.description,
    "offers": {
      "@type": "Offer",
      "price": cat.price,
      "priceCurrency": "AUD",
      "availability": "https://schema.org/InStock",
      "url": url
    }
  };
}

export function buildLocalBusinessSchema(service: any) {
  return {
    "@context": "https://schema.org",
    "@type": "VeterinaryCare",
    "name": service.name,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": service.address,
      "addressLocality": service.city,
      "addressRegion": service.state,
      "addressCountry": "AU"
    },
    "telephone": service.phone
  };
}
