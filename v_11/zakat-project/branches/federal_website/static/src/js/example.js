angular.module('plunker', ['ui.bootstrap']);
var ModalDemoCtrl = function ($scope) {
  $scope.stepBack = function () {
    $scope.currentStep -= 1;
  };
  
  $scope.stepForward = function () {
    $scope.currentStep += 1;
  };
  
  $scope.showStep = function (step) {
    return step == $scope.currentStep;
  };

  $scope.open = function () {
    $scope.shouldBeOpen = true;
    $scope.currentStep = 1;
  };

  $scope.close = function () {
    $scope.closeMsg = 'I was closed at: ' + new Date();
    $scope.shouldBeOpen = false;
  };

  $scope.items = ['item1', 'item2'];

  $scope.opts = {
    backdropFade: true,
    dialogFade:true
  };

};