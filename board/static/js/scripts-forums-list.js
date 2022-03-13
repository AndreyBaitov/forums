$(function(){
	$("body").on('click', '.close-category', function(){
		$(this).parents(".forums-header").next().css('display','none'); 			 /*вырубаем список форумов категории*/
		$(this).parents(".forums-header").css({'opacity':'0.3'});         			/* делаем полупрозрачной заголов */
		$(this).parents(".forums-container").css({'border':'2px solid #FAEAC6'});  /*делаем фоновым бордер, чтобы не выделялось по размеру*/
	});
	
	$("body").on('click', '.roll-button', function(){
		let dealing = $(this).parents(".forums-header").next().children()
		if (dealing.css('display') == 'none' ) {								/* если списка нет, значит показываем*/
			$(this).parents(".forums-header").next().css('display', 'flex'); 	/* Если этот элемент не вернуть, остальные тоже не возвращаются*/
			dealing.css('display', 'flex');
			$(this).text(String.fromCharCode(8722)); 							/* Это ставит - вместо +*/
			$(this).parents(".forums-header").css({'opacity':'1'});
			$(this).parents(".forums-container").css({'border':'2px solid #663333'});
			} 
		else {dealing.css('display', 'none');$(this).text('+');};   			/* Иначе список прячем, вышестоящей функцией, а тут просто меняем значок*/
	});

});