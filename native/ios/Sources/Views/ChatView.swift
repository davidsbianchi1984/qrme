import SwiftUI

/// The core loop: chat with the profile as an interactor. The interactor
/// identity is created lazily on first send and remembered; replies held by
/// moderation render as pending rather than silently vanishing.
struct ChatView: View {
    struct Bubble: Identifiable {
        let id = UUID()
        let mine: Bool
        let text: String
        let pending: Bool
    }

    @EnvironmentObject var state: AppState
    @State private var messages: [Bubble] = []
    @State private var draft = ""
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Chat").font(.title2.bold()).foregroundStyle(Theme.txt)
                        Text("Talk with \(state.displayName) — replies are in character and moderated.")
                            .font(.footnote).foregroundStyle(Theme.t2)

                        ForEach(messages) { m in
                            HStack {
                                if m.mine { Spacer(minLength: 40) }
                                Text(m.text)
                                    .font(.subheadline)
                                    .foregroundStyle(m.pending ? Theme.t2 : Theme.txt)
                                    .padding(.horizontal, 12).padding(.vertical, 9)
                                    .background(m.mine ? Theme.brandA.opacity(0.35)
                                                       : Theme.card.opacity(0.9))
                                    .clipShape(RoundedRectangle(cornerRadius: 13))
                                if !m.mine { Spacer(minLength: 40) }
                            }
                            .id(m.id)
                        }

                        if let error {
                            Text(error).font(.footnote).foregroundStyle(Theme.red)
                        }
                    }.padding(20)
                }
                .onChange(of: messages.count) { _ in
                    if let last = messages.last { proxy.scrollTo(last.id) }
                }
            }

            HStack(spacing: 10) {
                TextField("Say something…", text: $draft)
                    .foregroundStyle(Theme.txt)
                    .padding(.horizontal, 12).padding(.vertical, 10)
                    .background(Theme.scrBot)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
                    .overlay(RoundedRectangle(cornerRadius: 12).stroke(Theme.line, lineWidth: 1))
                Button(action: send) {
                    if busy { ProgressView().tint(.white) }
                    else { Image(systemName: "paperplane.fill") }
                }
                .frame(width: 44, height: 40)
                .background(Theme.brand).foregroundStyle(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .disabled(draft.isEmpty || busy)
            }
            .padding(.horizontal, 20).padding(.bottom, 12)
        }
    }

    private func send() {
        guard let pid = state.pid, let token = state.token else { return }
        let text = draft
        draft = ""
        messages.append(Bubble(mine: true, text: text, pending: false))
        busy = true; error = nil
        Task {
            do {
                // Lazily mint the device owner's interactor identity once.
                var interactor = state.interactorId
                if interactor == nil {
                    let created = try await ApiClient.shared.createInteractor(name: "You")
                    state.rememberInteractor(created.id)
                    interactor = created.id
                }
                let reply = try await ApiClient.shared.chat(
                    id: pid, token: token, interactorId: interactor!, message: text)
                let p = reply.profile_message
                if let content = p.content, p.status == "approved" {
                    messages.append(Bubble(mine: false, text: content, pending: false))
                } else {
                    messages.append(Bubble(
                        mine: false,
                        text: "⏳ Held for review" +
                              (p.flag_reason.map { " — \($0)" } ?? ""),
                        pending: true))
                }
            } catch {
                self.error = error.localizedDescription
            }
            busy = false
        }
    }
}
