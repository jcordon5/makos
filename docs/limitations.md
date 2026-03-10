# Limitaciones de la POC

- búsqueda basada en texto/similitud superficial (sin embeddings)
- prevención de duplicados no semántica avanzada
- no hay control de concurrencia multi-proceso sobre el mismo archivo
- no hay permisos OS-level; la gobernanza es por convención + validación
- no incluye plugin Obsidian obligatorio ni automatizaciones UI
- la capa de skills runtime implementada de forma nativa en esta POC está orientada primero a Claude-compatible `SKILL.md`
