import SwiftUI

/// Robotic embodiment: bind a catalog robot to the profile and command it.
/// The same persona speaks through the body; "say" is generated in character
/// and moderated server-side before it is ever spoken.
struct RobotsView: View {
    @EnvironmentObject var state: AppState
    @State private var catalog: [RobotSpec] = []
    @State private var chosen = "neo"
    @State private var robots: [Robot] = []
    @State private var topic = ""
    @State private var lastResult: String?
    @State private var busy = false
    @State private var error: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Robots").font(.title2.bold()).foregroundStyle(Theme.txt)
                Text("Same persona · a physical body. Commands follow a per-body allowlist.")
                    .font(.footnote).foregroundStyle(Theme.t2)

                VStack(alignment: .leading, spacing: 10) {
                    Text("Bind a robot").font(.headline).foregroundStyle(Theme.txt)
                    Picker("", selection: $chosen) {
                        ForEach(catalog, id: \.model) {
                            Text("\($0.label) · \($0.maker)").tag($0.model)
                        }
                    }.pickerStyle(.menu).tint(Theme.brandA)
                    Button(action: bind) {
                        HStack { if busy { ProgressView().tint(.white) }; Text("Bind").bold() }
                            .frame(maxWidth: .infinity).padding(.vertical, 12)
                            .background(Theme.brand).foregroundStyle(.white)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }.disabled(busy || catalog.isEmpty)
                }.card()

                if let error { Text(error).font(.footnote).foregroundStyle(Theme.red) }

                if !robots.isEmpty {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Topic for \"say\"").font(.caption).foregroundStyle(Theme.t2)
                        TextField("What should it speak about?", text: $topic)
                            .foregroundStyle(Theme.txt)
                            .padding(10).background(Theme.scrBot)
                            .clipShape(RoundedRectangle(cornerRadius: 11))
                            .overlay(RoundedRectangle(cornerRadius: 11).stroke(Theme.line, lineWidth: 1))
                    }.card()
                }

                ForEach(robots, id: \.id) { r in
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(r.name).font(.subheadline.bold()).foregroundStyle(Theme.txt)
                            Spacer()
                            Text((r.status ?? "docked").capitalized)
                                .font(.caption).foregroundStyle(Theme.t2)
                        }
                        HStack(spacing: 8) {
                            let cmds = r.commands ?? []
                            if cmds.contains("say") {
                                actionButton("Say") { command(r, "say", topic) }
                            }
                            if cmds.contains("clean") {
                                actionButton("Clean") { command(r, "clean", nil) }
                            }
                            if cmds.contains("patrol") {
                                actionButton("Patrol") { command(r, "patrol", nil) }
                            }
                            actionButton("Dock") { command(r, "dock", nil) }
                        }
                    }.card()
                }

                if let lastResult {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("Result").font(.headline).foregroundStyle(Theme.txt)
                        Text(lastResult).font(.subheadline).foregroundStyle(Theme.txt)
                    }.card()
                }
            }.padding(20)
        }
        .task { await load() }
    }

    private func actionButton(_ label: String, _ action: @escaping () -> Void) -> some View {
        Button(label, action: action)
            .font(.caption.bold()).foregroundStyle(.white)
            .padding(.horizontal, 12).padding(.vertical, 7)
            .background(Theme.brandA).clipShape(Capsule())
    }

    private func load() async {
        guard let pid = state.pid, let token = state.token else { return }
        catalog = (try? await ApiClient.shared.roboticsCatalog())?.robots ?? []
        robots = (try? await ApiClient.shared.robots(id: pid, token: token)) ?? []
    }

    private func bind() {
        guard let pid = state.pid, let token = state.token else { return }
        busy = true; error = nil
        Task {
            do { _ = try await ApiClient.shared.bindRobot(id: pid, token: token, model: chosen) }
            catch { self.error = error.localizedDescription }
            await load(); busy = false
        }
    }

    private func command(_ robot: Robot, _ cmd: String, _ arg: String?) {
        guard let token = state.token else { return }
        error = nil
        Task {
            do {
                let r = try await ApiClient.shared.commandRobot(
                    rid: robot.id, token: token, command: cmd, arg: arg)
                lastResult = r.spoken ?? "\(r.command): \(r.status)"
            } catch { self.error = error.localizedDescription }
            await load()
        }
    }
}
