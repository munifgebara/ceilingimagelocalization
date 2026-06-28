---
name: nova-tarefa
description: Fluxo padrão de trabalho do projeto — cria issue no GitHub, abre branch, implementa, abre Pull Request para a master, aprova e faz o merge. Use sempre que for iniciar uma nova tarefa/feature/correção neste repositório.
---

# Nova tarefa (issue → branch → PR → merge)

Toda mudança neste projeto segue este fluxo. **Nunca commite direto na `master`.**

## Passos

1. **Criar a issue** (título e corpo em português):
   ```bash
   gh issue create --title "<título da tarefa>" \
     --body "<descrição: objetivo, contexto, critérios de aceite>"
   ```
   Anote o número retornado (ex.: `#7`).

2. **Criar o branch** a partir da `master` atualizada:
   ```bash
   git switch master && git pull --ff-only
   git switch -c <tipo>/<resumo-curto>   # tipo: feat | fix | docs | chore | refactor
   ```

3. **Implementar** com commits pequenos e mensagens em português:
   ```bash
   git add -A
   git commit -m "<mensagem clara em português>"
   ```
   Rode os testes/lint antes de seguir: `make test && make lint`.

4. **Abrir o Pull Request** para a `master`, referenciando a issue:
   ```bash
   git push -u origin HEAD
   gh pr create --base master --title "<título>" \
     --body "Closes #<N>\n\n<resumo das mudanças>"
   ```

5. **Aprovar e fazer o merge** (squash):
   ```bash
   gh pr review --approve
   gh pr merge --squash --delete-branch
   ```

6. **Voltar para a master** e confirmar que a issue foi fechada:
   ```bash
   git switch master && git pull --ff-only
   gh issue view <N>
   ```

## Convenções

- Mensagens de commit em português, no imperativo: "Adiciona endpoint de saúde".
- Um PR por issue, pequeno e focado.
- Sempre `make test` e `make lint` antes de abrir o PR.
