import SwiftUI
import Engine

struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            HomeView(onStart: { path.append(Route.game) })
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .game: GameView()
                    }
                }
        }
    }

    enum Route: Hashable { case game }
}

private struct HomeView: View {
    let onStart: () -> Void
    @AppStorage("hasSeenTutorialIntro") private var hasSeenTutorialIntro: Bool = false
    @State private var showingTutorial: Bool = false

    var body: some View {
        ZStack {
            Theme.lanai.ignoresSafeArea()
            VStack(spacing: 28) {
                Spacer()
                VStack(spacing: 6) {
                    Text("Mahjong+×")
                        .font(.custom(Theme.displayFont, size: 56))
                        .foregroundStyle(Theme.windInk)
                    Text("Practice solo. Play sharper.")
                        .font(.system(size: 14, weight: .medium, design: .rounded))
                        .foregroundStyle(Theme.goldDeep.opacity(0.85))
                }
                Spacer()
                Button(action: handleStart) {
                    Text("Start a Run")
                        .font(.system(size: 18, weight: .semibold, design: .rounded))
                        .padding(.horizontal, 36)
                        .padding(.vertical, 14)
                        .background(
                            RoundedRectangle(cornerRadius: 16)
                                .fill(Theme.gold)
                                .shadow(color: Theme.shadow.opacity(0.5), radius: 6, y: 4)
                        )
                        .foregroundStyle(.white)
                }
                .buttonStyle(.plain)

                Button(action: { showingTutorial = true }) {
                    Text("How to play")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundStyle(Theme.goldDeep.opacity(0.8))
                        .underline()
                }
                .buttonStyle(.plain)

                Text("MVP — Tables 1 & 2")
                    .font(.system(size: 11, weight: .medium))
                    .foregroundStyle(Theme.shadow)
                Spacer()
            }
            .padding()
        }
        .overlay {
            if showingTutorial {
                ZStack {
                    Color.black.opacity(0.55).ignoresSafeArea()
                    TutorialIntroCard {
                        showingTutorial = false
                        hasSeenTutorialIntro = true
                    }
                }
                .transition(.opacity)
            }
        }
        .onAppear {
            if !hasSeenTutorialIntro {
                showingTutorial = true
            }
        }
        .navigationBarHidden(true)
    }

    private func handleStart() {
        // Auto-mark tutorial seen if user dives in without reading.
        hasSeenTutorialIntro = true
        onStart()
    }
}

#Preview { ContentView() }
