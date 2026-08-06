import SwiftUI

/// The derivation trail under persona-generated content: which model spoke,
/// what it was grounded in, licensed lineage, and the moderation verdict —
/// nothing the platform emits is a black box.
struct ProvenanceFooter: View {
    let provenance: ContentProvenance
    let lang: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Divider().overlay(Theme.line)
            Text(L10n.fill("nprv.generated", lang,
                           ["model": provenance.generated_by,
                            "n": "\(provenance.grounded_in.source_items)",
                            "status": provenance.moderation.status]))
                .font(.caption2).foregroundStyle(Theme.t2)
            if let lineage = provenance.licensed_from {
                Text(L10n.fill("nprv.licensed", lang, ["source": lineage])).font(.caption2).foregroundStyle(Theme.amber)
            }
            Text(provenance.disclaimer).font(.caption2).foregroundStyle(Theme.t3)
        }
    }
}
