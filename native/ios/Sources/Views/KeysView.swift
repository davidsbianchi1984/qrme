import SwiftUI

/// The keys, the till and the lifeline, in the pocket: the account that
/// owns everything here, the money that moves through it, and the app's
/// own status and help.
///
/// The rules these sections render rather than invent:
///
/// * **The address is proven before sign-in works.** Signup emails a
///   code; the code mints the first session; an unverified address
///   cannot sign in at all.
/// * **No button here is an address oracle.** Resend and reset answer
///   the same whether or not the address has an account.
/// * **The price list is public** — a paywall nobody can read the terms
///   of before signing in is one people bounce off.
/// * **Nothing bills on a timer.** Renewing a subscription is explicit
///   and names the beneficiary every time.
/// * **A donor gives to the names on the proceeds list,** not to the
///   platform — so the list is anyone's to read.
/// * **Help writes nothing** and is public on purpose: every screen can
///   be somebody's first.
struct KeysSection: View {
    @EnvironmentObject var state: AppState
    @State private var email = ""
    @State private var password = ""
    @State private var name = ""
    @State private var code = ""
    @State private var newPassword = ""
    @State private var oauthState = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("acct.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            TextField(L10n.t("acct.email", state.language), text: $email)
                .textFieldStyle(.roundedBorder)
            SecureField(L10n.t("acct.password", state.language),
                        text: $password)
                .textFieldStyle(.roundedBorder)
            HStack {
                TextField(L10n.t("acct.name", state.language), text: $name)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("acct.signup", state.language)) {
                    run {
                        let s = try await ApiClient.shared.signup(
                            email: email, password: password,
                            displayName: name)
                        line = s.code_delivery ?? "—"
                    }
                }.font(.caption).disabled(busy || email.isEmpty
                                          || password.isEmpty)
                Button(L10n.t("acct.signin", state.language)) {
                    run {
                        let s = try await ApiClient.shared.signin(
                            email: email, password: password)
                        line = s.display_name ?? s.email ?? "—"
                    }
                }.font(.caption).disabled(busy || email.isEmpty
                                          || password.isEmpty)
            }
            HStack {
                TextField(L10n.t("acct.code", state.language), text: $code)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("acct.verify", state.language)) {
                    run {
                        let s = try await ApiClient.shared.verifyEmail(
                            email: email, code: code)
                        line = s.email ?? "—"
                        code = ""
                    }
                }.font(.caption).disabled(busy || email.isEmpty
                                          || code.isEmpty)
                Button(L10n.t("acct.resend", state.language)) {
                    run {
                        let d = try await ApiClient.shared.resendCode(
                            email: email)
                        line = d.code_delivery ?? "—"
                    }
                }.font(.caption).disabled(busy || email.isEmpty)
            }
            HStack {
                Button(L10n.t("acct.reset.request", state.language)) {
                    run {
                        let d = try await ApiClient.shared
                            .requestPasswordReset(email: email)
                        line = d.code_delivery ?? "—"
                    }
                }.font(.caption).disabled(busy || email.isEmpty)
                SecureField(L10n.t("acct.reset.new", state.language),
                            text: $newPassword)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("acct.reset.do", state.language)) {
                    run {
                        let r = try await ApiClient.shared.resetPassword(
                            email: email, code: code,
                            newPassword: newPassword)
                        line = (r.reset ?? false) ? "✓" : "—"
                        newPassword = ""
                    }
                }.font(.caption).disabled(busy || email.isEmpty
                                          || code.isEmpty
                                          || newPassword.isEmpty)
            }
            HStack {
                Button(L10n.t("acct.oauth", state.language)) {
                    run {
                        let doors = try await ApiClient.shared
                            .oauthProviders().providers
                        if let first = doors.first {
                            let s = try await ApiClient.shared.oauthStart(
                                provider: first.provider)
                            oauthState = s.state ?? ""
                            line = first.provider + " · "
                                 + (s.url ?? "—")
                        } else { line = "—" }
                    }
                }.font(.caption).disabled(busy)
                if !oauthState.isEmpty {
                    Button("↻") {
                        run {
                            let c = try await ApiClient.shared.oauthClaim(
                                state: oauthState)
                            line = (c.ready ?? false)
                                 ? (c.email ?? "✓") : "…"
                        }
                    }.font(.caption).disabled(busy)
                }
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct TillSection: View {
    @EnvironmentObject var state: AppState
    @State private var subId = ""
    @State private var beneficiary = ""
    @State private var designee = ""
    @State private var campTitle = ""
    @State private var campGoal = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("till.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("till.plans", state.language)) {
                    run {
                        let c = try await ApiClient.shared.plans()
                        line = c.plans.map(\.plan).joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("till.subs", state.language)) {
                    run {
                        let l = try await ApiClient.shared.mySubscriptions(
                            token: state.token!)
                        line = "\(l.subscriptions.count)"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("till.orders", state.language)) {
                    run {
                        let l = try await ApiClient.shared.myOrders(
                            token: state.token!)
                        line = "\(l.orders.count)"
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                TextField(L10n.t("wrist.id", state.language), text: $subId)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("till.beneficiary", state.language),
                          text: $beneficiary)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("till.renew", state.language)) {
                    run {
                        let s = try await ApiClient.shared.renewSubscription(
                            subId: subId, beneficiary: beneficiary,
                            token: state.token!)
                        line = "\(s.periods ?? 0)"
                    }
                }.font(.caption).disabled(busy || subId.isEmpty
                                          || beneficiary.isEmpty)
            }
            HStack {
                Button(L10n.t("till.proceeds", state.language)) {
                    run {
                        let c = try await ApiClient.shared.proceedsOf(
                            id: state.pid!)
                        line = c.proceeds_to.map(\.name)
                            .joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("till.designees", state.language),
                          text: $designee)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("till.set", state.language)) {
                    run {
                        _ = try await ApiClient.shared.setProceeds(
                            id: state.pid!,
                            designees: [["name": designee,
                                         "kind": "loved_one",
                                         "share": 100]],
                            token: state.token!)
                        designee = ""
                        line = "✓"
                    }
                }.font(.caption).disabled(busy || designee.isEmpty)
            }
            HStack {
                Button(L10n.t("till.campaigns", state.language)) {
                    run {
                        let l = try await ApiClient.shared.campaignsOf(
                            id: state.pid!)
                        line = "\(l.count)"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("till.camp.title", state.language),
                          text: $campTitle)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("till.camp.goal", state.language),
                          text: $campGoal)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("till.camp.add", state.language)) {
                    run {
                        let c = try await ApiClient.shared.addCampaign(
                            id: state.pid!, title: campTitle,
                            goal: Double(campGoal) ?? 0, cause: "",
                            token: state.token!)
                        line = c.title ?? c.id
                        campTitle = ""; campGoal = ""
                    }
                }.font(.caption).disabled(busy || campTitle.isEmpty
                                          || campGoal.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}

struct LifelineSection: View {
    @EnvironmentObject var state: AppState
    @State private var question = ""
    @State private var provName = ""
    @State private var provArea = ""
    @State private var line: String?
    @State private var busy = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(L10n.t("life.title", state.language))
                .font(.headline).foregroundStyle(Theme.txt)
            HStack {
                Button(L10n.t("life.cloud", state.language)) {
                    run {
                        let c = try await ApiClient.shared.cloudStatus()
                        line = (c.cloud ? "☁" : "—") + " · "
                             + (c.fallback ?? "")
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("life.offline", state.language)) {
                    run {
                        let o = try await ApiClient.shared.offlineStatus()
                        line = o.provider ?? "—"
                    }
                }.font(.caption).disabled(busy)
                Button(L10n.t("life.lights", state.language)) {
                    run {
                        let l = try await ApiClient.shared.agentLights()
                        line = l.order.joined(separator: " · ")
                    }
                }.font(.caption).disabled(busy)
            }
            HStack {
                Button(L10n.t("life.help.topics", state.language)) {
                    run {
                        let t = try await ApiClient.shared.helpTopics()
                        line = "\(t.topics.count)"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("life.help", state.language),
                          text: $question)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("life.help.ask", state.language)) {
                    run {
                        let a = try await ApiClient.shared.askHelp(
                            question: question)
                        line = a.answer
                        question = ""
                    }
                }.font(.caption).disabled(busy || question.isEmpty)
            }
            HStack {
                Button(L10n.t("life.providers", state.language)) {
                    run {
                        let l = try await ApiClient.shared.localProviders()
                        line = "\(l.count)"
                    }
                }.font(.caption).disabled(busy)
                TextField(L10n.t("life.prov.name", state.language),
                          text: $provName)
                    .textFieldStyle(.roundedBorder)
                TextField(L10n.t("life.prov.area", state.language),
                          text: $provArea)
                    .textFieldStyle(.roundedBorder)
                Button(L10n.t("life.prov.add", state.language)) {
                    run {
                        let r = try await ApiClient.shared.addLocalProvider(
                            name: provName, area: provArea, location: "",
                            contact: "", business: true)
                        line = r.name ?? r.id
                        provName = ""; provArea = ""
                    }
                }.font(.caption).disabled(busy || provName.isEmpty
                                          || provArea.isEmpty)
            }
            if let line {
                Text(line).font(.caption2).foregroundStyle(Theme.t2)
            }
        }.card()
    }

    private func run(_ op: @escaping () async throws -> Void) {
        busy = true
        Task {
            do { try await op() }
            catch { line = error.localizedDescription }
            busy = false
        }
    }
}
