# MAKOS as a Claude Skill

MAKOS ahora se distribuye tambien como una skill Claude-compatible:

- source bundle: [agent-skills/makos-context-os/SKILL.md](../agent-skills/makos-context-os/SKILL.md)
- runtime target: `~/.claude/skills/makos-context-os`

## Qué consigue

Una vez habilitada, Claude puede tratar MAKOS como una capacidad persistente:

1. arrancar o reutilizar el vault compartido
2. buscar procedimientos y conocimiento antes de improvisar
3. escribir con trazabilidad y reglas de gobernanza
4. compartir memoria entre proyectos y agentes

## Flujo recomendado

1. Instalar MAKOS una vez: `./makos agent-ready --json`
2. En macOS, alternativa sin terminal: doble clic en `Install MAKOS.command`
3. Trabajar en cualquier otro workspace
4. Pedir tareas en lenguaje natural
5. Dejar que la skill `makos-context-os` active MAKOS por debajo

## Existing vaults

Si el usuario ya tiene un vault MAKOS existente, usar:

```bash
./makos --vault /ruta/al/vault agent-ready --json
```

Eso persiste el vault en la config global para futuras sesiones.
